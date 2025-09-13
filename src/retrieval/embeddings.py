"""
Embeddings Pipeline for Clinical Trial Matcher
Converts text to vectors for semantic search
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import json
import os
from tqdm import tqdm
import hashlib

class ClinicalEmbeddingPipeline:
    """
    Handles embedding generation and vector storage for trials and patients
    """
    def __init__(self,
                 model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
                 db_path: str = "./data/chromadb"):
        """
                Initialize embedding model and ChromaDB

                Args:
                    model_name: HuggingFace model for embeddings
                    db_path: Path for ChromaDB persistence
        """

        print(f"🚀 Initializing Embedding Pipeline...")

        # Initialize embedding model
        print(f"📦 Loading embedding model: {model_name}")
        self.encoder = SentenceTransformer(model_name)
        self.embedding_dim = self.encoder.get_sentence_embedding_dimension()
        print(f"✅ Model loaded (dimension: {self.embedding_dim})")
        #chromaDB Initialisation
        print(f"🗄️ Setting up ChromaDB at: {db_path}")
        self.chroma_client = chromadb.PersistentClient(
            path = db_path,
            settings = Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        self.trials_collection = self.chroma_client.get_or_create_collection(
            name="clinical_trials",
            metadata={"description": "Clinical trials with eligibility criteria"},
            embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=model_name
            )
        )
        print(f"✅ ChromaDB initialized with {self.trials_collection.count()} existing trials")

    def create_trial_embedding_text(self, trial: pd.Series) -> str:
        """
               Create rich text representation of trial for embedding

               Args:
                   trial: Row from trials DataFrame

               Returns:
                   Concatenated text for embedding
        """

        text_parts = [
            f"Title: {trial.get('title', '')}",
            f"Summary: {trial.get('summary', '')}",
            f"Conditions: {trial.get('conditions', '')}",
            f"Phase: {trial.get('phase', '')}",
            f"Eligibility: {trial.get('eligibility_criteria', '')}",
            f"Age Range: {trial.get('min_age', 'Any')} to {trial.get('max_age', 'Any')}",
            f"Gender: {trial.get('gender', 'All')}",
            f"Study Type: {trial.get('study_type', '')}"
        ]

        return " | ".join(filter(None, text_parts))

    def create_patient_query_text(self, patient: Dict[str, Any]) -> str:
        """
                Create query text from patient profile

                Args:
                    patient: Patient profile dictionary

                Returns:
                    Text representation for embedding
        """

        text_parts = [
            f"Age: {patient.get('age', '')} years old",
            f"Gender: {patient.get('gender', '')}",
            f"Conditions: {patient.get('conditions', '')}",
            f"Current medications: {patient.get('medications', '')}",
            f"Previous treatments: {patient.get('previous_treatments', 'None')}",
            f"Location: {patient.get('location_city', '')}, {patient.get('location_state', '')}",
        ]

        if patient.get('biomarkers'):
            biomarkers = patient['biomarkers']
            if isinstance(biomarkers, str):
                text_parts.append(f"Biomarkers: {biomarkers}")
            elif isinstance(biomarkers, dict):
                biomarker_text = ", ".join([f"{k}: {v}" for k, v in biomarkers.items()])
                text_parts.append(f"Biomarkers: {biomarker_text}")

        if patient.get('stage'):
            text_parts.append(f"Stage: {patient['stage']}")

        if patient.get('performance_status'):
            text_parts.append(f"Performance: {patient['performance_status']}")

        return " | ".join(filter(None, text_parts))

    def embed_trials(self, trials_df: pd.DataFrame, batch_size: int = 32) -> None:
        """
                Embed all trials and store in ChromaDB

                Args:
                    trials_df: DataFrame with trial data
                    batch_size: Number of trials to process at once
                """
        print(f"\n📊 Embedding {len(trials_df)} trials...")

        documents = []
        metadatas = []
        ids = []

        for idx, trial in tqdm(trials_df.iterrows(), total=len(trials_df), desc="Preparing trials"):
            # Create embedding text
            doc_text = self.create_trial_embedding_text(trial)
            documents.append(doc_text)

            # Create metadata (searchable attributes)
            metadata = {
                'nct_id': str(trial.get('nct_id', '')),
                'title': str(trial.get('title', ''))[:500],  # ChromaDB has metadata size limits
                'conditions': str(trial.get('conditions', ''))[:500],
                'status': str(trial.get('status', '')),
                'phase': str(trial.get('phase', '')),
                'min_age': str(trial.get('min_age', '')),
                'max_age': str(trial.get('max_age', '')),
                'gender': str(trial.get('gender', '')),
                'locations': str(trial.get('locations', ''))[:500]
            }
            metadatas.append(metadata)

            # Use NCT ID as unique identifier
            ids.append(str(trial.get('nct_id', f'trial_{idx}')))

            # Add to ChromaDB in batches
        print("💾 Storing embeddings in ChromaDB...")

        # Clear existing trials if any (for clean testing)
        if self.trials_collection.count() > 0:
            print("🧹 Clearing existing trials...")
            self.trials_collection.delete(ids=self.trials_collection.get()['ids'])

        # Add new trials
        for i in range(0, len(documents), batch_size):
            batch_end = min(i + batch_size, len(documents))

            self.trials_collection.add(
                documents=documents[i:batch_end],
                metadatas=metadatas[i:batch_end],
                ids=ids[i:batch_end]
            )

            print(f"  Added batch {i // batch_size + 1}/{(len(documents) - 1) // batch_size + 1}")

        print(f"✅ Successfully embedded {len(documents)} trials!")
        print(f"📈 Collection now contains {self.trials_collection.count()} trials")

    def find_matching_trials(self,
                             patient: Dict[str, Any],
                             n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Find best matching trials for a patient

        Args:
            patient: Patient profile dictionary
            n_results: Number of top matches to return

        Returns:
            List of matched trials with similarity scores
        """
        # Create patient query text
        query_text = self.create_patient_query_text(patient)

        print(f"\n🔍 Searching for matches...")
        print(f"Patient: {patient.get('patient_id', 'Unknown')}")
        print(f"Query: {query_text[:100]}...")

        # Search in ChromaDB
        results = self.trials_collection.query(
            query_texts=[query_text],
            n_results=n_results
        )

        # Format results
        matches = []
        if results['ids'] and len(results['ids'][0]) > 0:
            for i in range(len(results['ids'][0])):
                match = {
                    'nct_id': results['ids'][0][i],
                    'similarity_score': 1 - results['distances'][0][i],  # Convert distance to similarity
                    'title': results['metadatas'][0][i].get('title', ''),
                    'conditions': results['metadatas'][0][i].get('conditions', ''),
                    'phase': results['metadatas'][0][i].get('phase', ''),
                    'locations': results['metadatas'][0][i].get('locations', ''),
                    'document': results['documents'][0][i]
                }
                matches.append(match)

        print(f"✅ Found {len(matches)} matching trials")
        return matches

    def test_retrieval(self,
                       patient_file: str = "data/raw/synthetic_patients.json",
                       n_results: int = 3):
        """
        Test retrieval with synthetic patients

        Args:
            patient_file: Path to synthetic patients file
            n_results: Number of matches per patient
        """
        print("\n" + "=" * 50)
        print("Testing Retrieval System")
        print("=" * 50)

        # Load synthetic patients
        with open(patient_file, 'r') as f:
            patients = json.load(f)

        # Test with first 2 patients
        for patient in patients[:2]:
            print(f"\n👤 Patient {patient['patient_id']}")
            print(f"   Condition: {patient['conditions']}")
            print(f"   Age: {patient['age']}, Gender: {patient['gender']}")

            # Find matches
            matches = self.find_matching_trials(patient, n_results=n_results)

            # Display results
            for i, match in enumerate(matches, 1):
                print(f"\n   Match {i}: {match['nct_id']}")
                print(f"   Similarity: {match['similarity_score']:.3f}")
                print(f"   Title: {match['title'][:100]}...")
                print(f"   Conditions: {match['conditions'][:100]}...")


if __name__ == "__main__":
    # Initialize pipeline
    pipeline = ClinicalEmbeddingPipeline()

    # Load trials data
    print("\n📂 Loading trials data...")



    # Load both cancer and diabetes trials
    trials_dfs = []
    print(f"DEBUG: Looking for files in: {os.getcwd()}/data/raw/")  # ADD THIS
    print(f"DEBUG: Files found: {os.listdir('data/raw/')}")  # ADD THIS
    for file in ['cancer_trials.csv', 'diabetes_trials.csv']:
        filepath = f'data/raw/{file}'
        if os.path.exists(filepath):
            df = pd.read_csv(filepath)
            trials_dfs.append(df)
            print(f"  Loaded {len(df)} trials from {file}")

    # Combine all trials
    if trials_dfs:
        all_trials = pd.concat(trials_dfs, ignore_index=True)
        print(f"📊 Total trials to embed: {len(all_trials)}")

        # Embed trials
        pipeline.embed_trials(all_trials)

        # Test retrieval
        if os.path.exists('data/raw/synthetic_patients.json'):
            pipeline.test_retrieval()
        else:
            print("⚠️ No synthetic patients found for testing")
    else:
        print("❌ No trial data found. Run clinical_trials_fetcher.py first!")