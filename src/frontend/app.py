"""
Streamlit UI for Clinical Trial Matcher
"""

import streamlit as st
import sys
import os
import json
import pandas as pd
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm.trial_matcher import TrialMatchingSystem
from data.synthetic_patients import SyntheticPatientGenerator

# Page config
st.set_page_config(
    page_title="Clinical Trial Matcher",
    page_icon="🏥",
    layout="wide"
)

# Initialize session state
if 'matching_system' not in st.session_state:
    st.session_state.matching_system = TrialMatchingSystem()


def main():
    st.title("🏥 Clinical Trial Matcher")
    st.markdown("*AI-powered clinical trial matching using RAG technology*")

    # Sidebar
    with st.sidebar:
        st.header("📋 Patient Information")

        input_method = st.radio(
            "Choose input method:",
            ["Use Sample Patient", "Enter Custom Details"]
        )

        if input_method == "Use Sample Patient":
            # Load synthetic patients
            if os.path.exists('data/raw/synthetic_patients.json'):
                with open('data/raw/synthetic_patients.json', 'r') as f:
                    patients = json.load(f)

                patient_options = {
                    f"Patient {p['patient_id']} - {p['conditions'][:50]}...": p
                    for p in patients
                }

                selected_patient_key = st.selectbox(
                    "Select a patient:",
                    options=list(patient_options.keys())
                )

                patient = patient_options[selected_patient_key]

                # Display patient details
                st.subheader("Patient Details")
                st.write(f"**Age:** {patient['age']} years")
                st.write(f"**Gender:** {patient['gender']}")
                st.write(f"**Conditions:** {patient['conditions']}")
                if patient.get('biomarkers'):
                    st.write(f"**Biomarkers:** {patient['biomarkers']}")
            else:
                st.error("No sample patients found!")
                patient = None

        else:  # Custom input
            patient = {}
            patient['patient_id'] = "CUSTOM001"
            patient['age'] = st.number_input("Age", min_value=18, max_value=100, value=55)
            patient['gender'] = st.selectbox("Gender", ["Male", "Female", "Other"])
            patient['conditions'] = st.text_area("Medical Conditions",
                                                 placeholder="e.g., Non-Small Cell Lung Cancer, Diabetes")
            patient['medications'] = st.text_area("Current Medications",
                                                  placeholder="e.g., Metformin, Insulin")
            patient['biomarkers'] = st.text_area("Biomarkers (if known)",
                                                 placeholder="e.g., PD-L1: 60%, EGFR: Positive")
            patient['location_city'] = st.text_input("City", value="Boston")
            patient['location_state'] = st.text_input("State", value="MA")
            patient['willing_to_travel'] = st.checkbox("Willing to travel for trials")

        # Search button
        search_button = st.button("🔍 Find Matching Trials", type="primary", use_container_width=True)

    # Main content area
    if search_button and patient:
        with st.spinner("🔬 Analyzing trials... This may take a moment..."):
            # Run matching
            matches = st.session_state.matching_system.match_patient_to_trials(
                patient,
                n_trials=5
            )

            if matches:
                st.success(f"✅ Found {len(matches)} potential matches!")

                # Display results in tabs
                tab1, tab2, tab3 = st.tabs(["📊 Match Results", "📝 Detailed Report", "❓ FAQs"])

                with tab1:
                    # Group by eligibility
                    eligible = [m for m in matches if m.eligibility_status == "ELIGIBLE"]
                    likely = [m for m in matches if m.eligibility_status == "LIKELY_ELIGIBLE"]
                    review = [m for m in matches if m.eligibility_status == "NEEDS_REVIEW"]

                    if eligible:
                        st.subheader("✅ Eligible Trials")
                        for match in eligible:
                            with st.expander(f"{match.nct_id} - {match.title[:60]}..."):
                                st.write(f"**Similarity Score:** {match.similarity_score:.3f}")
                                st.write("**Why you match:**")
                                for reason in match.match_reasons:
                                    st.write(f"• {reason}")
                                st.write("**Questions for your doctor:**")
                                for q in match.questions_for_doctor:
                                    st.write(f"• {q}")

                    if likely:
                        st.subheader("🔵 Likely Eligible Trials")
                        for match in likely:
                            with st.expander(f"{match.nct_id} - {match.title[:60]}..."):
                                st.write(f"**Similarity Score:** {match.similarity_score:.3f}")
                                st.write("**Potential concerns:**")
                                for concern in match.concerns:
                                    st.write(f"• {concern}")

                    if review:
                        st.subheader("🔍 Trials Needing Review")
                        for match in review:
                            with st.expander(f"{match.nct_id} - {match.title[:60]}..."):
                                st.write(f"**Similarity Score:** {match.similarity_score:.3f}")
                                st.write(f"**Status:** {match.explanation}")

                with tab2:
                    # Generate and display report
                    report = st.session_state.matching_system.generate_report(patient, matches)
                    st.text(report)

                    # Download button
                    st.download_button(
                        label="📥 Download Report",
                        data=report,
                        file_name=f"trial_matches_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain"
                    )

                with tab3:
                    st.subheader("Frequently Asked Questions")

                    with st.expander("How does the matching work?"):
                        st.write("""
                        Our system uses advanced AI to:
                        1. Convert your medical information into semantic vectors
                        2. Search a database of clinical trials for similar patterns
                        3. Use LLM to analyze specific eligibility criteria
                        4. Provide clear explanations of matches
                        """)

                    with st.expander("What do the eligibility statuses mean?"):
                        st.write("""
                        - **✅ ELIGIBLE**: You appear to meet all key criteria
                        - **🔵 LIKELY ELIGIBLE**: You meet most criteria but need clarification
                        - **🔍 NEEDS REVIEW**: Requires professional evaluation
                        - **❌ NOT ELIGIBLE**: You don't meet key requirements
                        """)

                    with st.expander("Should I contact trials directly?"):
                        st.write("""
                        Always discuss with your healthcare provider first. They can:
                        - Verify your eligibility
                        - Help you understand risks and benefits
                        - Assist with the enrollment process
                        """)
            else:
                st.warning("No matching trials found. Try adjusting your search criteria.")

    elif search_button:
        st.error("Please enter patient information first.")

    else:
        # Welcome message
        st.info("""
        👋 **Welcome to the Clinical Trial Matcher!**

        This tool helps patients find potentially suitable clinical trials based on their medical profile.

        **How to use:**
        1. Select a sample patient or enter custom details in the sidebar
        2. Click 'Find Matching Trials'
        3. Review your matches and download the report

        *Note: This is a demonstration tool. Always consult with healthcare professionals.*
        """)


if __name__ == "__main__":
    main()