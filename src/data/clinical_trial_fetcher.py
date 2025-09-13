"""
ClinicalTrails.gov API interface
Fetches and processes clinical trail data without requiring API keys
"""
import requests
import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime
import time

import requests.exceptions
from tqdm import tqdm
import json
import os

class ClinicalTrialsFetcher:
    """Fetches trail data from ClinicalTrials.gov API v2"""

    BASE_URL = "https://clinicaltrials.gov/api/v2/studies"

    def __init__(self, max_trials: int = 100):
        self.max_trials = max_trials
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ClinicalTrialMatcher/1.0'
        })
    def fetch_trials(self,
                     condition: Optional[str] = "cancer",
                     status: str = "RECRUITING"
                     ) -> pd.DataFrame:
        params = {
            'query.cond': condition,
            'filter.overallStatus': status,
            'pageSize': min(self.max_trials, 100),
            'format': 'json',
            'fields': 'NCTId,BriefTitle,BriefSummary,Condition,OverallStatus,EligibilityCriteria,Phase,StudyType,Gender,MinimumAge,MaximumAge,LocationCity,LocationState,LocationCountry'
        }
        print(f"🔍 Fetching {self.max_trials} trials for condition: {condition}")

        all_trials = []
        next_page_token = None

        while len(all_trials)<self.max_trials:
            try:
                if next_page_token:
                    params['pageToken'] = next_page_token

                response = self.session.get(self.BASE_URL, params = params, timeout=30)
                response.raise_for_status()
                data = response.json()

                studies = data.get('studies', [])
                if not studies:
                    break
                all_trials.extend(studies)

                next_page_token = data.get('nextPageToken')
                if not next_page_token:
                    break
                time.sleep(0.5)
            except requests.exceptions.RequestException as e:
                print(f"❌ Error fetching trials: {e}")
                break
        all_trials = all_trials[:self.max_trials]
        if all_trials:
            trials_df = self._parse_trials(all_trials)
            print(f"✅ Successfully fetched {len(trials_df)} trials")
            return trials_df
        else:
            print("❌ No trials found")
            return pd.DataFrame()


    def _parse_trials(self, studies: List[Dict]):
        """Parse raw API response into structured format"""

        parsed_trials = []

        for study in tqdm(studies, desc="Parsing trials"):
            protocol = study.get('protocolSection', {})

            # Extract identification info
            id_module = protocol.get('identificationModule', {})
            desc_module = protocol.get('descriptionModule', {})
            status_module = protocol.get('statusModule', {})
            conditions_module = protocol.get('conditionsModule', {})
            design_module = protocol.get('designModule', {})
            eligibility_module = protocol.get('eligibilityModule', {})
            contacts_module = protocol.get('contactsLocationsModule', {})

            # Extract locations
            locations = self._extract_locations(contacts_module)

            # Build trial record
            trial = {
                'nct_id': id_module.get('nctId', ''),
                'title': id_module.get('briefTitle', ''),
                'summary': desc_module.get('briefSummary', ''),
                'conditions': ', '.join(conditions_module.get('conditions', [])),
                'status': status_module.get('overallStatus', ''),
                'phase': ', '.join(design_module.get('phases', [])) if design_module.get('phases') else 'N/A',
                'study_type': design_module.get('studyType', 'N/A'),
                'eligibility_criteria': eligibility_module.get('eligibilityCriteria', 'Not specified'),
                'min_age': eligibility_module.get('minimumAge', 'N/A'),
                'max_age': eligibility_module.get('maximumAge', 'N/A'),
                'gender': eligibility_module.get('sex', 'ALL'),
                'healthy_volunteers': eligibility_module.get('healthyVolunteers', False),
                'locations': locations,
                'enrollment': design_module.get('enrollmentInfo', {}).get('count', 0) if design_module.get(
                    'enrollmentInfo') else 0
            }

            parsed_trials.append(trial)

        return pd.DataFrame(parsed_trials)

    def _extract_locations(self, contacts_module: Dict) -> str:
        """Extract trials locations"""
        locations = contacts_module.get('locations', [])

        if not locations:
            return "Not specified"
        location_strs = []
        for loc in locations[:5]:
            city = loc.get('city','')
            state = loc.get('state','')
            country = loc.get('country','')
            facility = loc.get('facility','')

            loc_parts = [facility, city, state, country]
            loc_str = ', '.join(filter(None, loc_parts))
            if loc_str:
                location_strs.append(loc_str)
        return ' | '.join(location_strs) if location_strs else 'Not specified'

    def save_trials(self, df: pd.DataFrame, filepath: str = 'data/raw/clinical_trials.csv'):
        """Save DataFrame into CSV"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        df.to_csv(filepath, index=False)
        print(f"💾 Saved {len(df)} trials to {filepath}")
        return filepath


if __name__ == "__main__":
    # Create fetcher instance
    fetcher = ClinicalTrialsFetcher(max_trials=10)

    # Fetch trials for different conditions
    print("\n" + "=" * 50)
    print("Testing Clinical Trials Fetcher")
    print("=" * 50)

    # Test 1: Cancer trials
    cancer_trials = fetcher.fetch_trials(condition="lung cancer", status="RECRUITING")

    if not cancer_trials.empty:
        print("\n📊 Sample Cancer Trial:")
        sample = cancer_trials.iloc[0]
        print(f"NCT ID: {sample['nct_id']}")
        print(f"Title: {sample['title'][:100]}...")
        print(f"Conditions: {sample['conditions']}")
        print(f"Phase: {sample['phase']}")
        print(f"Status: {sample['status']}")

        # Save the data
        fetcher.save_trials(cancer_trials, 'data/raw/cancer_trials.csv')

    # Test 2: Diabetes trials
    print("\n" + "-" * 50)
    diabetes_trials = fetcher.fetch_trials(condition="diabetes", status="RECRUITING")

    if not diabetes_trials.empty:
        print("\n📊 Sample Diabetes Trial:")
        sample = diabetes_trials.iloc[0]
        print(f"NCT ID: {sample['nct_id']}")
        print(f"Title: {sample['title'][:100]}...")

        fetcher.save_trials(diabetes_trials, 'data/raw/diabetes_trials.csv')

    print("\n✅ Testing complete! Check data/raw/ for saved trials.")