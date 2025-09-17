from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm.trial_matcher import TrialMatchingSystem

app = FastAPI()

# Enable CORS for Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize matching system
matching_system = TrialMatchingSystem()


class PatientRequest(BaseModel):
    age: int
    gender: str
    conditions: str
    medications: str = ""
    biomarkers: str = ""


@app.post("/match")
async def match_trials(patient: PatientRequest):
    try:
        patient_dict = patient.dict()
        patient_dict['patient_id'] = 'WEB001'

        matches = matching_system.match_patient_to_trials(patient_dict, n_trials=5)

        return {
            "message": "Analysis complete",
            "matches": [
                {
                    "nct_id": m.nct_id,
                    "title": m.title,
                    "status": m.eligibility_status,
                    "explanation": m.explanation,
                    "score": m.similarity_score
                }
                for m in matches
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)