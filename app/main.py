import io
import base64
from fastapi.responses import StreamingResponse
from fastapi import FastAPI
from app.config import TESTING_MODE
from fastapi.middleware.cors import CORSMiddleware
from app.schemas.patient import PatientData
from app.schemas.final_output import FinalResult
from app.schemas.chat import Messages
from app.services.uti_service import UTIService
from app.services.report_service import ReportService
from app.services.chat_service import ChatService

# Initialize FastAPI app
app = FastAPI(
    title="UTI Antibiotic Recommendation API",
    description="Predicts organism name and recommends antibiotics for UTI patients",
    version="1.0.0"
)

origins = [
    "http://localhost:8080",  # Your frontend
    "http://127.0.0.1:8080",  # Sometimes React uses this
    "https://ai-uti.netlify.app",  # Deployed frontend
    # You can add more origins here if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          
    allow_credentials=True,         
    allow_methods=["*"],            
    allow_headers=["*"],            
)

# Initialize the service (loads models once)
uti_service = UTIService()


@app.get("/health")
def health_check():
    return {"status": "UP", "message": "UTI Antibiotic Recommendation API is running."}


@app.post("/predict", response_model=FinalResult)
def predict_antibiotics(patient: PatientData):
    """
    Predict organism and recommend top antibiotics.
    Input: JSON payload of patient clinical data
    Output: JSON with predicted organism, resistance, sensitivity, and recommended antibiotics
    """
    if TESTING_MODE:
        return {
            "patient_index": 0,
            "patient_details": {
                "age": 37,
                "gender": "Female",
                "department": "Urology",
                "chief_complaints": "Burning urination;Urgency;Cloudy urine",
                "comorbidities": "",
                "riskfactors": "Poor hygiene",
                "surgical_history": "",
                "social_history": "Non smoker",
                "diagnosis": "Cystitis",
                "classification_of_uti": "Uncomplicated UTI",
                "type_of_uti": "Cystitis",
                "site_of_infection": "Lower Urinary Tract",
                "type_of_sample": "Urine",
                "previous_antibiotic_used": "Cotrimoxazole;Amoxicillin",
                "lab_results": {
                "cbp_lymphocytes": 36,
                "wbc": 9140,
                "polymorphs": 65,
                "crp": 9,
                "rft_serum_creatinine": 0.8,
                "serum_uric_acid": 4.2,
                "blood_urea": 26,
                "cue_pus_cells": 12,
                "epithelial_cells": 3,
                "proteins": "Trace",
                "rbc": 2
                }
            },
            "predictions": {
                "organism_name_prediction": "Escherichia coli",
                "bacteria_type_prediction": "Gram-negative bacillus (The primary cause of uncomplicated UTIs)",
                "predicted_resistant_antibiotics": [
                "Clarithromycin"
                ],
                "predicted_sensitive_antibiotics": [
                "Ciprofloxacin",
                "Norfloxacin"
                ]
            },
            "prescribed_antibiotics": {
                "recommended": [
                {
                    "name": "Ciprofloxacin",
                    "dosage": "500 mg orally twice daily for 3 days",
                    "precautions": "No known renal impairment (creatinine 0.8 mg/dL); no reported fluoroquinolone allergy. Use with caution in patients with a history of tendon disorders, QT prolongation, or concomitant use of drugs that may prolong QT. No dose adjustment needed for current renal function.",
                    "explanation": "Ciprofloxacin is a fluoroquinolone with excellent activity against Gram‑negative bacilli such as Escherichia coli and is listed as a predicted sensitive agent. It achieves high urinary concentrations, making it appropriate for uncomplicated cystitis."
                },
                {
                    "name": "Norfloxacin",
                    "dosage": "400 mg orally twice daily for 3 days",
                    "precautions": "Renal function normal; no known allergy to norfloxacin. Monitor for possible central nervous system side effects (e.g., dizziness, headache) and avoid in patients with a history of seizures or severe tendon disorders. No dose adjustment required at current creatinine level.",
                    "explanation": "Norfloxacin is a quinolone with strong activity against E. coli and attains therapeutic levels in urine. It is included in the predicted sensitive list and is suitable for treating uncomplicated lower urinary tract infection."
                }
                ]
            },
            "antibiotic_history": {
                "Ciprofloxacin": {
                "background": "A breakthrough second-generation fluoroquinolone introduced in 1987. It was the first oral antibiotic with potent activity against Pseudomonas aeruginosa, fundamentally changing the management of chronic infections in cystic fibrosis and nosocomial UTIs.",
                "common_usage": "Used for complicated UTIs, infectious diarrhea (Cipro is often 'the' travel antibiotic), bone and joint infections, and prophylaxis for meningococcal meningitis exposure. It is also a first-line agent for anthrax exposure.",
                "historical_success": "Ciprofloxacin's introduction led to a significant decrease in hospital length-of-stay for patients with serious Gram-negative infections, as they could be switched from IV aminoglycosides to oral Cipro tablets.",
                "mechanism_of_action": "Bactericidal action through the inhibition of DNA Gyrase (Topoisomerase II) and Topoisomerase IV. By preventing the supercoiling and untangling of bacterial DNA, it halts replication and causes the DNA to fragment.",
                "side_effects": "Subject to several 'Black Box' warnings from the FDA, including risk of tendon rupture (Achilles), permanent peripheral neuropathy, and CNS effects (delirium/seizures). It can also cause QT prolongation and should be avoided in pregnancy and children due to cartilage damage concerns.",
                "resistance_notes": "Resistance has skyrocketed due to over-prescription. E. coli resistance in some regions exceeds 30-50%. Resistance is usually chromosomal (gyrA mutations) but can be plasmid-mediated (qnr genes), which spreads rapidly between species."
                },
                "Norfloxacin": {
                "background": "The first 'fluoroquinolone' (a quinolone with a fluorine atom added). Approved in 1986, it was a massive improvement over nalidixic acid, though it was quickly surpassed by ciprofloxacin.",
                "common_usage": "Used almost exclusively for UTIs and for 'SBP' (Spontaneous Bacterial Peritonitis) prophylaxis in patients with liver cirrhosis. It does not reach high enough levels in the blood to treat other types of infections.",
                "historical_success": "Norfloxacin was the 'proof of concept' for the fluoroquinolone class. It showed that adding a fluorine atom drastically increased the drug's power and broadened its spectrum of activity.",
                "mechanism_of_action": "Inhibits DNA Gyrase and Topoisomerase IV. This prevents the bacteria from replicating their DNA, leading to a rapid stop in growth and eventually cell death.",
                "side_effects": "Shares the common fluoroquinolone risks: tendonitis, CNS issues, and photosensitivity. It is also known to interact with caffeine, making the effects of coffee last much longer in the body.",
                "resistance_notes": "Because it was used extensively in the 1990s, resistance is now very common among E. coli. It is generally considered 'weaker' than ciprofloxacin, so if a bacteria is resistant to norfloxacin, ciprofloxacin might still work, but not vice versa."
                }
            },
            "summary": "**Infection Summary:**  \n- **Type:** Uncomplicated cystitis (lower urinary‑tract infection).  \n- **Predicted pathogen:** *Escherichia coli* (Gram‑negative bacillus, the most common cause of uncomplicated UTIs).  \n\n**Antibiotic susceptibility:**  \n- **Resistant:** Clarithromycin (not effective against the predicted organism).  \n- **Sensitive (predicted):** Ciprofloxacin, Norfloxacin – both fluoroquinolones with reliable activity against *E. coli* and high urinary concentrations.\n\n**Recommended therapy:**  \n\n1. **Ciprofloxacin 500 mg PO BID × 3 days**  \n   - **Rationale:** Fluoroquinolone with excellent *E. coli* coverage; achieves therapeutic urine levels; aligns with predicted sensitivity.  \n   - **Precautions:** No renal dose adjustment needed (creatinine 0.8 mg/dL). Avoid in patients with tendon disorders, QT‑prolongation risk, or concurrent QT‑prolonging drugs. Verify absence of fluoroquinolone allergy.\n\n2. **Norfloxacin 400 mg PO BID × 3 days** (alternative)  \n   - **Rationale:** Similar spectrum and urinary penetration as ciprofloxacin; listed as a predicted sensitive agent.  \n   - **Precautions:** Normal renal function; monitor for CNS effects (dizziness, headache). Contraindicated in seizure history or severe tendon disease. No dose adjustment required.\n\n**Key considerations:**  \n- Prior antibiotics (cotrimoxazole, amoxicillin) were ineffective; fluoroquinolones are now preferred.  \n- Ensure patient education on adherence, potential tendon or CNS side effects, and to report any new musculoskeletal pain or cardiac symptoms promptly.  \n- Re‑evaluate if symptoms persist beyond 72 h or if culture results later contradict the prediction."
        }
    
    try:
        patient_dict = patient.model_dump()
        result = uti_service.generate_final_output(patient_dict)
        return result
            
    except Exception as e:
        raise e


@app.get("/patient_records")
def get_patient_records():
    return uti_service._load_patient_records()


@app.post("/generate_report")
def generate_report(results: dict):
    # Initialize report service
    report_service = ReportService()
    
    # Generate PDF as base64 string
    base64_pdf = report_service.generate_report(results)
    
    # Convert base64 to bytes
    pdf_bytes = io.BytesIO(base64.b64decode(base64_pdf))
    
    # Return as StreamingResponse
    return StreamingResponse(
        pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "inline; filename=finalreport.pdf"
        }
    )


@app.post("/chat")
def chat(messages: Messages):
    chat_service = ChatService()
    return chat_service.generate_response(messages.messages)