from app.inference.uti_inference import BacteriaInferenceEngine
from app.services.llm_service import LLMService
from app.config import MODEL_DIR
from app.utils.llm_prompts import PROMPT_FOR_PRECRIBED_ANTIBIOTICS, PROMPT_FOR_ANTIBIOTIC_HISTORY, PROMPT_FOR_SUMMARY

class UTIService:
    def __init__(self):
        """
        Load the inference class and models once during service initialization
        """
        # Initialize inference class with paths
        self.uti_system = BacteriaInferenceEngine(model_dir=MODEL_DIR)
        self.llm_service = LLMService()


    def predict(self, patient_data: dict):
        """
        Predict bacteria type and recommend antibiotics
        :param patient_data: Dictionary of patient input
        :return: Dictionary with predicted bacteria, resistance probabilities, top antibiotics
        """
        # Run the inference class
        result = self.uti_system.predict(patient_data)
        return {
            "patient_index" : result[0]["patient_index"],
            "bacteria_type_prediction": result[0]["bacteria_type_prediction"],
            "predicted_resistant_antibiotics": result[0]["predicted_resistant_antibiotics"],
            "predicted_sensitive_antibiotics": result[0]["predicted_sensitive_antibiotics"]
        }    

    def get_precribed_antibiotics(self, patient_data: dict, predictions: dict)-> dict:
        system_prompt = PROMPT_FOR_PRECRIBED_ANTIBIOTICS
        user_prompt = {
            "patient_data": patient_data,
            "predictions": predictions
        }
        return self.llm_service.invoke_llm(system_prompt, user_prompt)
    
    def get_antibiotic_history(self, antibiotics: list) -> dict:
        system_prompt = PROMPT_FOR_ANTIBIOTIC_HISTORY
        user_prompt = {
            "antibiotics": antibiotics
        }
        return self.llm_service.invoke_llm(system_prompt, user_prompt)

    def get_summary(self, patient_data: dict, predictions: dict, prescribed_antibiotics: list, antibiotic_history: dict) -> str:
        system_prompt = PROMPT_FOR_SUMMARY
        user_prompt = {
            "patient_data": patient_data,
            "predictions": predictions,
            "prescribed_antibiotics": prescribed_antibiotics,
            "antibiotic_history": antibiotic_history
        }
        return self.llm_service.invoke_llm(system_prompt, user_prompt)

    def generate_final_output(self, patient_data : dict) -> dict:
        predictions = self.predict(patient_data)
        predictions.pop("patient_index", None)  # Remove patient_index from predictions as it's not needed for subsequent steps
        normalized_patient_data = {k.lower(): v for k, v in patient_data.items()}  # Normalize keys to lowercase
        prescribed_antibiotics = self.get_precribed_antibiotics(normalized_patient_data, predictions)
        prescribed_antibiotics_details = {
            "patient_index": 0,
            "prescribed_antibiotics": [antibiotic["name"] for antibiotic in prescribed_antibiotics["recommended"]]
        }
        antibiotic_history = self.get_antibiotic_history(prescribed_antibiotics_details)
        summary = self.get_summary(patient_data, predictions, prescribed_antibiotics, antibiotic_history)
        
        cbp_lymphocytes = normalized_patient_data.pop("cbp_lymphocytes", None)
        wbc = normalized_patient_data.pop("wbc", None)
        polymorphs = normalized_patient_data.pop("polymorphs", None)
        crp = normalized_patient_data.pop("crp", None)
        rft_serum_creatinine = normalized_patient_data.pop("rft_serum_creatinine", None)
        serum_uric_acid = normalized_patient_data.pop("serum_uric_acid", None)
        blood_urea = normalized_patient_data.pop("blood_urea", None)
        cue_pus_cells = normalized_patient_data.pop("cue_pus_cells", None)
        epithelial_cells = normalized_patient_data.pop("epithelial_cells", None)
        proteins = normalized_patient_data.pop("proteins", None)
        rbc = normalized_patient_data.pop("rbc", None)

        return {
            "patient_index": 0,
            "patient_details": {
                **normalized_patient_data,
                "lab_results": {
                    "cbp_lymphocytes": cbp_lymphocytes,
                    "wbc": wbc,
                    "polymorphs": polymorphs,
                    "crp": crp,
                    "rft_serum_creatinine": rft_serum_creatinine,
                    "serum_uric_acid": serum_uric_acid,
                    "blood_urea": blood_urea,
                    "cue_pus_cells": cue_pus_cells,
                    "epithelial_cells": epithelial_cells,
                    "proteins": proteins,
                    "rbc": rbc
                }
            },
            "predictions": predictions,
            "prescribed_antibiotics": prescribed_antibiotics,
            "antibiotic_history": antibiotic_history,
            "summary": summary
        }
