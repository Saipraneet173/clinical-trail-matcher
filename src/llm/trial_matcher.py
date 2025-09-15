"""
LLM-powered Trial Matching and Explanation System
Uses Llama 3.2 via Groq for intelligent eligibility analysis
"""

import os
import sys
import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import pandas as pd
from groq import Groq
from dotenv import load_dotenv
import time

# Fix import path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Now this import should work
from retrieval.embeddings import ClinicalEmbeddingPipeline

# Load environment variables
load_dotenv()

@dataclass
class MatchResult:
    """Structure for trial match results with explanations"""
    nct_id: str
    title: str
    similarity_score: float
    eligibility_status: str  # ELIGIBLE, LIKELY_ELIGIBLE, NOT_ELIGIBLE, NEEDS_REVIEW
    match_reasons: List[str]
    concerns: List[str]
    questions_for_doctor: List[str]
    explanation: str


class TrialMatchingSystem:
    """
    Orchestrates the complete matching pipeline:
    1. Semantic search for relevant trials
    2. LLM analysis of eligibility
    3. Human-readable explanations
    """

    def __init__(self, groq_api_key: Optional[str] = None):
        print("🚀 Initializing Trial Matching System...")

        # Fix: Use correct path for ChromaDB
        current_file = os.path.abspath(__file__)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
        db_path = os.path.join(project_root, "data", "chromadb")

        # Initialize embedding pipeline with correct path
        self.embedding_pipeline = ClinicalEmbeddingPipeline(db_path=db_path)

        # Initialize Groq client
        api_key = groq_api_key or os.getenv('GROQ_API_KEY')
        if not api_key:
            print("⚠️ Warning: No Groq API key found. Set GROQ_API_KEY in .env file")
            print("   Get your free key at: https://console.groq.com")
            print("   Running in demo mode without LLM explanations...")
            self.client = None
        else:
            self.client = Groq(api_key=api_key)
            print("✅ Groq client initialized")

    def create_analysis_prompt(self, patient: Dict[str, Any], trial: Dict[str, Any]) -> str:
        """
        Create a detailed prompt for LLM analysis

        Args:
            patient: Patient profile
            trial: Trial information

        Returns:
            Formatted prompt for the LLM
        """
        prompt = f"""You are a clinical trial matching expert. Analyze if this patient is eligible for the trial.

PATIENT PROFILE:
- Age: {patient.get('age')} years old
- Gender: {patient.get('gender')}
- Primary Condition: {patient.get('conditions', 'Not specified')}
- Current Medications: {patient.get('medications', 'None listed')}
- Previous Treatments: {patient.get('previous_treatments', 'None listed')}
- Biomarkers: {patient.get('biomarkers', 'Not specified')}
- Performance Status: {patient.get('performance_status', 'Not specified')}
- Location: {patient.get('location_city')}, {patient.get('location_state')}
- Willing to Travel: {patient.get('willing_to_travel', False)}

CLINICAL TRIAL:
- Title: {trial.get('title')}
- NCT ID: {trial.get('nct_id')}
- Conditions Studied: {trial.get('conditions')}
- Phase: {trial.get('phase')}
- Eligibility Criteria: {trial.get('eligibility_criteria', 'Not specified')[:1000]}
- Age Range: {trial.get('min_age', 'No minimum')} to {trial.get('max_age', 'No maximum')}
- Gender Requirement: {trial.get('gender', 'All')}
- Locations: {trial.get('locations', 'Not specified')[:500]}

TASK:
1. Determine eligibility status: ELIGIBLE, LIKELY_ELIGIBLE, NOT_ELIGIBLE, or NEEDS_REVIEW
2. List specific reasons why the patient matches or doesn't match
3. Identify any concerns or missing information
4. Suggest questions the patient should ask their doctor
5. Provide a brief, clear explanation in simple language

Respond in JSON format:
{{
    "eligibility_status": "ELIGIBLE/LIKELY_ELIGIBLE/NOT_ELIGIBLE/NEEDS_REVIEW",
    "match_reasons": ["reason1", "reason2"],
    "concerns": ["concern1", "concern2"],
    "questions_for_doctor": ["question1", "question2"],
    "explanation": "Simple language explanation for the patient"
}}
NO Preamble.
"""

        return prompt

    def analyze_with_llm(self, patient: Dict[str, Any], trial: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use LLM to analyze trial eligibility

        Args:
            patient: Patient profile
            trial: Trial information

        Returns:
            Analysis results from LLM
        """
        if not self.client:
            # Demo mode without LLM
            return {
                "eligibility_status": "NEEDS_REVIEW",
                "match_reasons": ["Semantic similarity detected"],
                "concerns": ["LLM analysis not available in demo mode"],
                "questions_for_doctor": ["Please review this trial with your doctor"],
                "explanation": "This trial appears relevant based on keyword matching. Please consult your healthcare provider for detailed eligibility assessment."
            }

        try:
            prompt = self.create_analysis_prompt(patient, trial)

            # Call Groq API
            completion = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",  # Fast, free tier model
                messages=[
                    {"role": "system",
                     "content": "You are a medical expert who helps patients understand clinical trial eligibility. Always respond in valid JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent output
                max_tokens=500
            )

            # Parse response
            response_text = completion.choices[0].message.content

            # Try to extract JSON from response
            try:
                # Find JSON in response (sometimes LLM adds extra text)
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    result = json.loads(response_text)

                # Validate required fields
                required_fields = ['eligibility_status', 'match_reasons', 'concerns',
                                   'questions_for_doctor', 'explanation']
                for field in required_fields:
                    if field not in result:
                        result[
                            field] = [] if field != 'eligibility_status' and field != 'explanation' else "NEEDS_REVIEW"

                return result

            except json.JSONDecodeError:
                print(f"⚠️ Could not parse LLM response as JSON")
                return {
                    "eligibility_status": "NEEDS_REVIEW",
                    "match_reasons": ["Analysis completed but format unclear"],
                    "concerns": ["Response parsing issue"],
                    "questions_for_doctor": ["Please review the full trial details with your doctor"],
                    "explanation": response_text[:200] if response_text else "Analysis unavailable"
                }

        except Exception as e:
            print(f"⚠️ LLM analysis error: {str(e)}")
            return {
                "eligibility_status": "NEEDS_REVIEW",
                "match_reasons": ["Automated analysis unavailable"],
                "concerns": [f"Technical issue: {str(e)[:100]}"],
                "questions_for_doctor": ["Please review this trial with your healthcare provider"],
                "explanation": "Unable to complete automated analysis. Please consult your doctor."
            }

    def match_patient_to_trials(self,
                                patient: Dict[str, Any],
                                n_trials: int = 5,
                                min_similarity: float = -0.5) -> List[MatchResult]:
        """
        Complete matching pipeline for a patient

        Args:
            patient: Patient profile
            n_trials: Number of trials to analyze
            min_similarity: Minimum similarity score to consider

        Returns:
            List of MatchResult objects with explanations
        """
        print(f"\n🔬 Analyzing matches for Patient {patient.get('patient_id', 'Unknown')}")

        # Step 1: Semantic search for relevant trials
        semantic_matches = self.embedding_pipeline.find_matching_trials(patient, n_results=n_trials)

        if not semantic_matches:
            print("❌ No matching trials found")
            return []

        # Step 2: Load full trial data
        # In production, this would query a database
        # For now, we'll use the semantic match data
        results = []

        for i, match in enumerate(semantic_matches, 1):
            print(f"\n  Analyzing trial {i}/{len(semantic_matches)}: {match['nct_id']}")

            # Skip if similarity too low
            if match['similarity_score'] < min_similarity:
                print(f"  ⏭️ Skipping (similarity {match['similarity_score']:.3f} below threshold)")
                continue

            # Add eligibility criteria from the document field
            # (In production, we'd fetch full trial details from database)
            trial_data = {
                'nct_id': match['nct_id'],
                'title': match['title'],
                'conditions': match['conditions'],
                'phase': match['phase'],
                'locations': match['locations'],
                'eligibility_criteria': match['document']  # This contains our embedded text
            }

            # Step 3: LLM analysis
            if self.client:
                print("  🤖 Running LLM analysis...")
                time.sleep(0.5)  # Rate limiting for free tier

            analysis = self.analyze_with_llm(patient, trial_data)

            # Step 4: Create result
            result = MatchResult(
                nct_id=match['nct_id'],
                title=match['title'],
                similarity_score=match['similarity_score'],
                eligibility_status=analysis['eligibility_status'],
                match_reasons=analysis['match_reasons'],
                concerns=analysis['concerns'],
                questions_for_doctor=analysis['questions_for_doctor'],
                explanation=analysis['explanation']
            )

            results.append(result)

            # Display summary
            status_emoji = {
                'ELIGIBLE': '✅',
                'LIKELY_ELIGIBLE': '🔵',
                'NOT_ELIGIBLE': '❌',
                'NEEDS_REVIEW': '🔍'
            }

            print(f"  {status_emoji.get(result.eligibility_status, '❓')} Status: {result.eligibility_status}")
            print(f"  📊 Similarity: {result.similarity_score:.3f}")

        return results

    def generate_report(self, patient: Dict[str, Any], matches: List[MatchResult]) -> str:
        """
        Generate a human-readable report

        Args:
            patient: Patient profile
            matches: List of match results

        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 60)
        report.append("CLINICAL TRIAL MATCHING REPORT")
        report.append("=" * 60)

        # Patient summary
        report.append(f"\n👤 PATIENT INFORMATION")
        report.append(f"ID: {patient.get('patient_id', 'N/A')}")
        report.append(f"Age: {patient.get('age')} | Gender: {patient.get('gender')}")
        report.append(f"Primary Condition: {patient.get('conditions', 'Not specified')}")

        if patient.get('biomarkers'):
            biomarkers_str = json.dumps(patient['biomarkers']) if isinstance(patient['biomarkers'], dict) else str(
                patient['biomarkers'])
            report.append(f"Biomarkers: {biomarkers_str}")

        report.append(f"\n📋 TRIALS ANALYZED: {len(matches)}")
        report.append("-" * 60)

        # Group by eligibility status
        eligible = [m for m in matches if m.eligibility_status == 'ELIGIBLE']
        likely = [m for m in matches if m.eligibility_status == 'LIKELY_ELIGIBLE']
        review = [m for m in matches if m.eligibility_status == 'NEEDS_REVIEW']
        not_eligible = [m for m in matches if m.eligibility_status == 'NOT_ELIGIBLE']

        # Report eligible trials first
        if eligible:
            report.append(f"\n✅ ELIGIBLE TRIALS ({len(eligible)})")
            for match in eligible:
                report.append(f"\n  Trial: {match.nct_id}")
                report.append(f"  Title: {match.title[:80]}...")
                report.append(f"  Match Score: {match.similarity_score:.3f}")
                report.append(f"  Why you match:")
                for reason in match.match_reasons[:3]:
                    report.append(f"    • {reason}")
                report.append(
                    f"  Next steps: {match.questions_for_doctor[0] if match.questions_for_doctor else 'Discuss with your doctor'}")

        # Then likely eligible
        if likely:
            report.append(f"\n🔵 LIKELY ELIGIBLE TRIALS ({len(likely)})")
            for match in likely:
                report.append(f"\n  Trial: {match.nct_id}")
                report.append(f"  Title: {match.title[:80]}...")
                report.append(f"  Needs clarification:")
                for concern in match.concerns[:2]:
                    report.append(f"    • {concern}")

        # Summary
        report.append("\n" + "=" * 60)
        report.append("SUMMARY")
        report.append(f"✅ Eligible: {len(eligible)} trials")
        report.append(f"🔵 Likely Eligible: {len(likely)} trials")
        report.append(f"🔍 Needs Review: {len(review)} trials")
        report.append(f"❌ Not Eligible: {len(not_eligible)} trials")

        report.append("\n💡 NEXT STEPS:")
        report.append("1. Review eligible trials with your healthcare provider")
        report.append("2. Prepare questions about specific eligibility criteria")
        report.append("3. Contact trial coordinators for more information")

        return "\n".join(report)


# Test the system
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Testing LLM-Powered Trial Matching System")
    print("=" * 60)

    # Fix: Use absolute path to find the file
    current_file = os.path.abspath(__file__)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
    patient_file_path = os.path.join(project_root, 'data', 'raw', 'synthetic_patients.json')

    # DEBUG
    print(f"\nDEBUG: Project root: {project_root}")
    print(f"DEBUG: Looking for: {patient_file_path}")
    print(f"DEBUG: File exists: {os.path.exists(patient_file_path)}")

    # Initialize system
    system = TrialMatchingSystem()

    # Load test patient
    if os.path.exists(patient_file_path):
        with open(patient_file_path, 'r') as f:
            patients = json.load(f)

        # Test with first patient
        test_patient = patients[1]  # Use patient with NSCLC

        # Run matching
        matches = system.match_patient_to_trials(test_patient, n_trials=3)

        # Generate report
        if matches:
            report = system.generate_report(test_patient, matches)
            print("\n" + report)

            # Save report with absolute path
            report_dir = os.path.join(project_root, 'data', 'processed')
            os.makedirs(report_dir, exist_ok=True)
            report_path = os.path.join(report_dir, 'sample_matching_report.txt')

            with open(report_path, 'w') as f:
                f.write(report)
            print(f"\n💾 Report saved to: {report_path}")
    else:
        print(f"❌ File not found at: {patient_file_path}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Files in project data/raw/: {os.listdir(os.path.join(project_root, 'data', 'raw'))}")