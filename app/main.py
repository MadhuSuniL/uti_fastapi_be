from fastapi import FastAPI
from app.config import TESTING_MODE
from fastapi.middleware.cors import CORSMiddleware
from app.schemas.patient import PatientData
from app.schemas.final_output import FinalResult
from app.schemas.chat import Messages
from app.services.uti_service import UTIService
from app.services.chat_service import ChatService

# Initialize FastAPI app
app = FastAPI(
    title="UTI Antibiotic Recommendation API",
    description="Predicts bacteria type and recommends antibiotics for UTI patients",
    version="1.0.0"
)

origins = [
    "http://localhost:8080",  # Your frontend
    "http://127.0.0.1:8080",  # Sometimes React uses this
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


@app.get("/")
def health_check():
    return {"status": "UP", "message": "UTI Antibiotic Recommendation API is running."}


@app.post("/predict", response_model=FinalResult)
def predict_antibiotics(patient: PatientData):
    """
    Predict bacteria and recommend top antibiotics.
    Input: JSON payload of patient clinical data
    Output: JSON with predicted bacteria, resistance, sensitivity, and recommended antibiotics
    """
    if TESTING_MODE:
        return {
            "patient_index": 0,
            "patient_details": {
                "age": 52,
                "gender": "Male",
                "department": "Urology",
                "chief_complaints": "Fever;Flank pain;Dysuria",
                "comorbidities": "Diabetes",
                "riskfactors": "Catheterization",
                "surgical_history": "No",
                "social_history": "Non smoker",
                "diagnosis": "Acute pyelonephritis",
                "classification_of_uti": "Complicated",
                "type_of_uti": "Acute",
                "site_of_infection": "Upper UTI",
                "type_of_sample": "Urine",
                "previous_antibiotic_used": "Ciprofloxacin",
                "lab_results": {
                    "cbp_lymphocytes": 24,
                    "wbc": 18200,
                    "polymorphs": 78,
                    "crp": 65,
                    "rft_serum_creatinine": 2.1,
                    "serum_uric_acid": 6.2,
                    "blood_urea": 48,
                    "cue_pus_cells": 28,
                    "epithelial_cells": 6,
                    "proteins": "Trace",
                    "rbc": 6
                }
            },
            "predictions": {
                "bacteria_type_prediction": "Gram Negative",
                "predicted_resistant_antibiotics": [
                    "Cefixime",
                    "Ciprofloxacin"
                ],
                "predicted_sensitive_antibiotics": [
                    "Amikacin",
                    "Cefepime",
                    "Piperacillin-Tazobactam"
                ]
            },
            "prescribed_antibiotics": {
                "recommended": [
                    {
                        "name": "Amikacin",
                        "dosage": "15 mg/kg IV once daily (adjust to every 48 h if CrCl <40 mL/min); monitor peak/trough levels",
                        "precautions": "Renal impairment (serum creatinine 2.1 mg/dL) – dose adjustment required; high nephrotoxic and ototoxic potential, monitor renal function and audiometry; ensure no known aminoglycoside allergy",
                        "explanation": "Amikacin is a potent aminoglycoside active against Gram‑negative organisms and is listed as sensitive. It provides excellent urinary excretion for pyelonephritis, and dose can be safely adjusted for the patient’s moderate renal dysfunction."
                    },
                    {
                        "name": "Cefepime",
                        "dosage": "1 g IV every 12 hours (adjusted for CrCl 30–50 mL/min); may be given over 30 min",
                        "precautions": "Renally excreted – reduce interval due to elevated creatinine; monitor for neurotoxicity in renal failure; check for β‑lactam allergy",
                        "explanation": "Cefepime is a fourth‑generation cephalosporin with strong activity against Gram‑negative pathogens, including those causing complicated UTIs. It is on the sensitive list and can be dosed safely with renal adjustment."
                    },
                    {
                        "name": "Piperacillin‑Tazobactam",
                        "dosage": "3.375 g IV every 6 hours (adjust to every 8 hours if CrCl 30–50 mL/min)",
                        "precautions": "Renal dosing required due to creatinine 2.1 mg/dL; monitor renal function and watch for hypersensitivity reactions; caution in patients with a history of penicillin allergy",
                        "explanation": "Piperacillin‑tazobactam offers broad Gram‑negative coverage, including ESBL‑producing organisms, and is effective for complicated upper urinary tract infections. It is predicted to be sensitive and can be used with appropriate renal dose adjustment."
                    }
                ]
            },
            "antibiotic_history": {
                "Amikacin": {
                    "background": "Amikacin is an aminoglycoside antibiotic derived from kanamycin, introduced in the 1970s to combat resistant gram‑negative organisms.",
                    "common_usage": "Used for serious infections caused by multidrug‑resistant gram‑negative bacteria such as Pseudomonas aeruginosa, Acinetobacter spp., and Enterobacteriaceae, often in combination therapy for sepsis or hospital‑acquired pneumonia.",
                    "historical_success": "Clinical trials and decades of use have demonstrated high bactericidal activity against resistant gram‑negative pathogens, maintaining efficacy where many β‑lactams fail.",
                    "mechanism_of_action": "Binds irreversibly to the 30S ribosomal subunit, causing misreading of mRNA and inhibition of protein synthesis, leading to rapid bacterial cell death.",
                    "side_effects": "Nephrotoxicity (dose‑related renal impairment), ototoxicity (vestibular and auditory), neuromuscular blockade, and rare allergic reactions.",
                    "resistance_notes": "Resistance arises mainly via enzymatic modification (acetyltransferases, phosphotransferases), efflux pumps, or 16S rRNA methylation; however, amikacin retains activity against many aminoglycoside‑modifying enzymes that inactivate other agents."
                },
                "Cefepime": {
                    "background": "Cefepime is a fourth‑generation cephalosporin introduced in the early 1990s, designed to broaden gram‑negative coverage while retaining gram‑positive activity.",
                    "common_usage": "Empiric treatment of febrile neutropenia, hospital‑acquired pneumonia, urinary tract infections, intra‑abdominal infections, and as part of combination therapy for severe sepsis.",
                    "historical_success": "Large multicenter studies have shown cefepime to be non‑inferior to carbapenems for many nosocomial infections, with a favorable safety profile.",
                    "mechanism_of_action": "Inhibits bacterial cell‑wall synthesis by binding to penicillin‑binding proteins (PBPs), particularly PBP‑3, leading to cell lysis; it is stable against many β‑lactamases, including AmpC.",
                    "side_effects": "Generally well tolerated; possible adverse effects include rash, gastrointestinal upset, transient elevation of liver enzymes, and rare Clostridioides difficile infection.",
                    "resistance_notes": "Resistance may develop via extended‑spectrum β‑lactamases (ESBLs), carbapenemases, or porin loss combined with efflux; susceptibility testing is essential for ESBL‑producing organisms."
                },
                "Piperacillin‑Tazobactam": {
                    "background": "Piperacillin is an extended‑spectrum ureidopenicillin; tazobactam is a β‑lactamase inhibitor. The combination was approved in the 1990s to broaden activity against β‑lactamase‑producing organisms.",
                    "common_usage": "Broad‑spectrum empiric therapy for intra‑abdominal infections, diabetic foot infections, severe skin‑soft tissue infections, and hospital‑acquired pneumonia, often used in critically ill patients.",
                    "historical_success": "Extensive clinical data support its efficacy in polymicrobial infections, with outcomes comparable to carbapenems for many indications when ESBL prevalence is low.",
                    "mechanism_of_action": "Piperacillin inhibits cell‑wall synthesis by binding PBPs; tazobactam irreversibly binds and inactivates many class A β‑lactamases, protecting piperacillin from degradation.",
                    "side_effects": "Common adverse effects include diarrhea, rash, transient elevations in liver enzymes, thrombocytopenia, and electrolyte disturbances (hypokalemia). Nephrotoxicity is rare but can occur with high doses.",
                    "resistance_notes": "Resistance emerges via production of ESBLs, AmpC β‑lactamases not inhibited by tazobactam, carbapenemases, or alterations in porin channels; routine susceptibility testing is recommended, especially in regions with high ESBL rates."
                }
            },
            "summary": "**Infection & Predicted Pathogen**  \n- Complicated acute pyelonephritis (upper UTI) in a 52‑year‑old diabetic male with recent catheterization.  \n- Predictive model suggests a Gram‑negative organism; resistance is anticipated to cefixime and ciprofloxacin, while amikacin, cefepime, and piperacillin‑tazobactam are predicted sensitive.\n\n**Resistance / Sensitivity Profile**  \n- **Resistant:** Cefixime, Ciprofloxacin (previously used).  \n- **Sensitive (predicted):** Amikacin, Cefepime, Piperacillin‑Tazobactam.\n\n**Recommended Regimen**  \n\n| Agent | Dose & Route | Rationale | Key Precautions |\n|-------|--------------|-----------|-----------------|\n| **Amikacin** | 15 mg/kg IV once daily (extend to q48 h if CrCl < 40 mL/min); monitor peak/trough levels | Potent aminoglycoside active against resistant Gram‑negatives; excellent urinary excretion for pyelonephritis. | Adjust for renal impairment (serum creatinine 2.1 mg/dL); monitor renal function, audiometry; avoid if known aminoglycoside allergy. |\n| **Cefepime** | 1 g IV q12 h (dose‑adjust for CrCl 30‑50 mL/min); infuse over 30 min | Fourth‑generation cephalosporin with broad Gram‑negative coverage, including many ESBL‑producers; suitable for complicated UTI. | Reduce interval for reduced clearance; watch for neurotoxicity in renal failure; β‑lactam allergy check. |\n| **Piperacillin‑Tazobactam** | 3.375 g IV q6 h (extend to q8 h if CrCl 30‑50 mL/min) | Provides broad‑spectrum β‑lactam/β‑lactamase inhibition, covering ESBL‑producing Enterobacteriaceae; effective for severe upper UTI. | Renal dose adjustment required; monitor renal function; assess for penicillin allergy; observe for hypersensitivity reactions. |\n\n**Overall Considerations**  \n- Renal dosing is critical given creatinine 2.1 mg/dL; all agents require interval or dose modification.  \n- Monitor for aminoglycoside nephro‑/ototoxicity and cefepime‑related neurotoxicity.  \n- Ensure no β‑lactam or aminoglycoside hypersensitivity before initiation.  \n- Re‑culture urine after 48‑72 h of therapy to confirm susceptibility and guide de‑escalation."
        }
    
    try:
        patient_dict = patient.model_dump()
        result = uti_service.generate_final_output(patient_dict)
        return result
            
    except Exception as e:
        raise e

@app.post("/chat")
def chat(messages: Messages):
    chat_service = ChatService()
    return chat_service.generate_response(messages.messages)