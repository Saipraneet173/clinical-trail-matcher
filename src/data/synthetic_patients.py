"""
Synthetic Patient Generator for Testing
Creates realistic patient profiles for clinical trial matching
"""

import json
import random
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import pandas as pd
from dataclasses import dataclass, asdict
import os

@dataclass
class PatientProfile:
    """Patient profile data structure"""
    patient_id: str
    age: int
    gender: str
    conditions: List[str]
    medications: List[str]
    allergies: List[str]
    previous_treatments: List[str]
    location_city: str
    location_state: str
    location_country: str
    willing_to_travel: bool
    diagnosis_date: str
    stage: Optional[str]
    biomarkers: Dict[str, str]
    comorbidities: List[str]
    performance_status: str  # ECOG score for cancer patients
    notes: str

class SyntheticPatientGenerator:
    """Generates realistic synthetic patient profiles for testing"""

    CANCER_TYPES = [
        "Non-Small Cell Lung Cancer", "Small Cell Lung Cancer",
        "Breast Cancer", "Colorectal Cancer", "Melanoma",
        "Pancreatic Cancer", "Prostate Cancer", "Leukemia"
    ]

    DIABETES_TYPES = [
        "Type 2 Diabetes", "Type 1 Diabetes",
        "Gestational Diabetes", "Prediabetes"
    ]

    CANCER_STAGES = ["Stage I", "Stage II", "Stage III", "Stage IV"]

    CANCER_MEDICATIONS = [
        "Carboplatin", "Paclitaxel", "Pembrolizumab", "Nivolumab",
        "Docetaxel", "Gemcitabine", "Cisplatin", "Bevacizumab"
    ]

    DIABETES_MEDICATIONS = [
        "Metformin", "Insulin Glargine", "Sitagliptin", "Empagliflozin",
        "Glimepiride", "Liraglutide", "Pioglitazone", "Insulin Aspart"
    ]

    COMMON_ALLERGIES = [
        "Penicillin", "Sulfa drugs", "Aspirin", "Iodine",
        "Latex", "None known"
    ]

    CANCER_BIOMARKERS = {
        "EGFR": ["Positive", "Negative", "Wild Type", "Mutated"],
        "ALK": ["Positive", "Negative", "Rearranged"],
        "PD-L1": ["<1%", "1-49%", "≥50%"],
        "KRAS": ["Wild Type", "G12C", "G12D", "G12V"],
        "HER2": ["Positive", "Negative", "Equivocal"]
    }

    DIABETES_MARKERS = {
        "HbA1c": ["6.5%", "7.2%", "8.1%", "9.3%", "10.5%", "11.2%"],
        "Fasting Glucose": ["126 mg/dL", "145 mg/dL", "168 mg/dL", "195 mg/dL"],
        "BMI": ["25.3", "28.7", "31.2", "34.5", "37.8"]
    }

    COMORBIDITIES = [
        "Hypertension", "Hyperlipidemia", "COPD", "Asthma",
        "Chronic Kidney Disease", "Heart Disease", "Osteoporosis",
        "Depression", "Anxiety", "None"
    ]

    ECOG_SCORES = [
        "0 - Fully active",
        "1 - Restricted in strenuous activity",
        "2 - Ambulatory, capable of self-care",
        "3 - Limited self-care",
        "4 - Completely disabled"
    ]

    LOCATIONS = [
        ("New York", "NY", "USA"),
        ("Los Angeles", "CA", "USA"),
        ("Chicago", "IL", "USA"),
        ("Houston", "TX", "USA"),
        ("Boston", "MA", "USA"),
        ("Atlanta", "GA", "USA"),
        ("Seattle", "WA", "USA"),
        ("Denver", "CO", "USA"),
        ("Miami", "FL", "USA"),
        ("Phoenix", "AZ", "USA")
    ]

    def __init__(self):
        self.patient_counter =  1000

    def generator_cancer_patient(self) -> PatientProfile:

        age = random.randint(35,85)
        gender = random.choice(["Male", "Female"])

        primary_cancer = random.choice(self.CANCER_TYPES)
        stage = random.choice(self.CANCER_STAGES) if "Leukemia" not in primary_cancer else None

        conditions = [primary_cancer]
        if random.random() > 0.3:
            conditions.extend(random.sample(self.COMORBIDITIES, k=random.randint(1,3)))

        medications = random.sample(self.CANCER_MEDICATIONS, k=random.randint(1,4))

        biomarkers = {}
        for marker in random.sample(list(self.CANCER_BIOMARKERS.keys()), k=random.randint(2,4)):
            biomarkers[marker] = random.choice(self.CANCER_BIOMARKERS[marker])

        location = random.choice(self.LOCATIONS)

        days_since_diagnosis = random.randint(30,1095)
        diagnosis_date = (datetime.now() - timedelta(days=days_since_diagnosis)).strftime("%Y-%m-%d")

        previous_treatments = []
        if days_since_diagnosis>180:
            previous_treatments = [
                f"Chemotherapy - {random.choice(['Completed', 'Partial', 'Discontinued'])}",
                f"Radiation - {random.choice(['Completed', 'Ongoing', 'Planned'])}"
            ]
        patient = PatientProfile(
            patient_id=f"P{self.patient_counter:04d}",
            age=age,
            gender=gender,
            conditions=conditions,
            medications=medications,
            allergies=random.sample(self.COMMON_ALLERGIES, k=random.randint(0, 2)),
            previous_treatments=previous_treatments,
            location_city=location[0],
            location_state=location[1],
            location_country=location[2],
            willing_to_travel=random.choice([True, False]),
            diagnosis_date=diagnosis_date,
            stage=stage,
            biomarkers=biomarkers,
            comorbidities=[c for c in conditions if c != primary_cancer],
            performance_status=random.choice(self.ECOG_SCORES[:3]),  # Usually 0-2 for trial eligibility
            notes=f"Patient interested in clinical trials for {primary_cancer}. " +
                  (f"Stage {stage}. " if stage else "") +
                  f"ECOG {self.ECOG_SCORES.index(random.choice(self.ECOG_SCORES[:3]))}."
        )

        self.patient_counter += 1
        return patient

    def generate_diabetes_patient(self) -> PatientProfile:
        """Generate a synthetic diabetes patient"""

        # Basic demographics
        age = random.randint(25, 80)
        gender = random.choice(["Male", "Female"])

        # Diabetes specifics
        diabetes_type = random.choice(self.DIABETES_TYPES)

        # Medical history
        conditions = [diabetes_type]
        if random.random() > 0.2:  # 80% have comorbidities
            conditions.extend(random.sample(self.COMORBIDITIES, k=random.randint(1, 4)))

        # Medications
        medications = random.sample(self.DIABETES_MEDICATIONS, k=random.randint(1, 3))

        # Diabetes markers
        biomarkers = {}
        biomarkers["HbA1c"] = random.choice(self.DIABETES_MARKERS["HbA1c"])
        biomarkers["Fasting Glucose"] = random.choice(self.DIABETES_MARKERS["Fasting Glucose"])
        biomarkers["BMI"] = random.choice(self.DIABETES_MARKERS["BMI"])

        # Location
        location = random.choice(self.LOCATIONS)

        # Diagnosis timeline
        days_since_diagnosis = random.randint(180, 3650)  # 6 months to 10 years
        diagnosis_date = (datetime.now() - timedelta(days=days_since_diagnosis)).strftime("%Y-%m-%d")

        # Previous treatments
        previous_treatments = []
        if days_since_diagnosis > 365:
            previous_treatments = [
                "Lifestyle modification program",
                f"Metformin - {random.choice(['Ongoing', 'Discontinued due to GI issues', 'Ineffective'])}"
            ]

        # Create patient profile
        patient = PatientProfile(
            patient_id=f"P{self.patient_counter:04d}",
            age=age,
            gender=gender,
            conditions=conditions,
            medications=medications,
            allergies=random.sample(self.COMMON_ALLERGIES, k=random.randint(0, 1)),
            previous_treatments=previous_treatments,
            location_city=location[0],
            location_state=location[1],
            location_country=location[2],
            willing_to_travel=random.choice([True, True, False]),  # More likely to travel for diabetes
            diagnosis_date=diagnosis_date,
            stage=None,  # Not applicable for diabetes
            biomarkers=biomarkers,
            comorbidities=[c for c in conditions if c != diabetes_type],
            performance_status="0 - Fully active",  # Most diabetes patients are ambulatory
            notes=f"Patient with {diabetes_type}, seeking better glycemic control. " +
                  f"Current HbA1c: {biomarkers['HbA1c']}. " +
                  f"Interested in novel diabetes therapies."
        )

        self.patient_counter += 1
        return patient

    def generate_batch(self, n_cancer: int = 5, n_diabetes: int = 5) -> List[PatientProfile]:
        """Generates a batch of mixed patient profiles"""
        patients = []

        for _ in range(n_cancer):
            patients.append(self.generator_cancer_patient())

        for _ in range(n_diabetes):
            patients.append(self.generate_diabetes_patient())
        return patients

    def save_patients(self, patients: List[PatientProfile],
                      filepath : str = 'data/raw/synthetic_patients.json'):
        """Saves patient profiles to JSON"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        # Convert to dictionary format
        patients_dict = []
        for patient in patients:
            patient_dict = asdict(patient)
            # Convert lists and dicts to JSON strings for better readability
            patient_dict['conditions'] = ', '.join(patient.conditions)
            patient_dict['medications'] = ', '.join(patient.medications)
            patient_dict['allergies'] = ', '.join(patient.allergies) if patient.allergies else 'None'
            patient_dict['previous_treatments'] = ' | '.join(
                patient.previous_treatments) if patient.previous_treatments else 'None'
            patient_dict['comorbidities'] = ', '.join(patient.comorbidities) if patient.comorbidities else 'None'
            patients_dict.append(patient_dict)

        # Save as JSON
        with open(filepath, 'w') as f:
            json.dump(patients_dict, f, indent=2)

        # Also save as CSV for easy viewing
        csv_filepath = filepath.replace('.json', '.csv')
        pd.DataFrame(patients_dict).to_csv(csv_filepath, index=False)

        print(f"💾 Saved {len(patients)} synthetic patients to:")
        print(f"   - {filepath}")
        print(f"   - {csv_filepath}")

        return filepath, csv_filepath


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("Generating Synthetic Patient Profiles")
    print("=" * 50)

    generator = SyntheticPatientGenerator()

    # Generate batch of patients
    patients = generator.generate_batch(n_cancer=5, n_diabetes=5)

    # Display sample patients
    print("\n📊 Sample Cancer Patient:")
    cancer_patient = patients[0]
    print(f"ID: {cancer_patient.patient_id}")
    print(f"Age: {cancer_patient.age}, Gender: {cancer_patient.gender}")
    print(f"Primary Condition: {cancer_patient.conditions[0]}")
    print(f"Stage: {cancer_patient.stage}")
    print(f"Biomarkers: {cancer_patient.biomarkers}")
    print(f"Location: {cancer_patient.location_city}, {cancer_patient.location_state}")

    print("\n📊 Sample Diabetes Patient:")
    diabetes_patient = patients[5]
    print(f"ID: {diabetes_patient.patient_id}")
    print(f"Age: {diabetes_patient.age}, Gender: {diabetes_patient.gender}")
    print(f"Primary Condition: {diabetes_patient.conditions[0]}")
    print(f"HbA1c: {diabetes_patient.biomarkers.get('HbA1c', 'N/A')}")
    print(f"Medications: {diabetes_patient.medications}")

    # Save patients
    generator.save_patients(patients)

    print("\n✅ Synthetic patients generated successfully!")
    print("Check data/raw/ for synthetic_patients.json and .csv files")