import pandas as pd
import numpy as np
import joblib
import os
import json

def squeeze_column(x):
    """
    Prevents 'TypeError: iteration over a 0-d array' by ensuring 
    the text transformer always receives a 1D array of strings.
    """
    if isinstance(x, (pd.DataFrame, pd.Series)):
        return x.values.astype(str).flatten()
    return np.array(x).astype(str).flatten()

class BacteriaInferenceEngine:
    def __init__(self, model_dir="."):
        """
        Initializes the engine and attaches the squeeze function to the 
        global namespace so joblib can find it during deserialization.
        """
        import __main__
        __main__.squeeze_column = squeeze_column
        
        try:
            # Load Model 1 (Bacteria Type)
            self.model_1 = joblib.load(os.path.join(model_dir, "model_1_bacteria.pkl"))
            
            # Load Model 2 (Resistance)
            self.model_2 = joblib.load(os.path.join(model_dir, "model_2_resistance.pkl"))
            self.mlb_2 = joblib.load(os.path.join(model_dir, "model_2_resistance_mlb.pkl"))
            
            # Load Model 3 (Sensitivity)
            self.model_3 = joblib.load(os.path.join(model_dir, "model_3_sensitivity.pkl"))
            self.mlb_3 = joblib.load(os.path.join(model_dir, "model_3_sensitive_mlb.pkl"))
            
            # Load shared Previous Antibiotic MultiLabelBinarizer
            self.prev_abx_mlb = joblib.load(os.path.join(model_dir, "prev_abx_mlb.pkl"))
            
            print("Successfully loaded all UTI diagnostic models.")
        except Exception as e:
            print(f"Initialization Error: {e}")

    def _preprocess(self, df):
        """Cleans columns and expands multi-label features."""
        df.columns = df.columns.str.strip().str.upper()
        
        # Numeric Type Casting
        numeric_cols = [
            'AGE', 'CBP_LYMPHOCYTES', 'WBC', 'POLYMORPHS', 'CRP', 
            'RFT_SERUM_CREATININE', 'SERUM_URIC_ACID', 'BLOOD_UREA', 
            'CUE_PUS_CELLS', 'EPITHELIAL_CELLS', 'RBC'
        ]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Multi-Label expansion for Previous Antibiotics
        if 'PREVIOUS_ANTIBIOTIC_USED' in df.columns:
            df['PREVIOUS_ANTIBIOTIC_USED'] = df['PREVIOUS_ANTIBIOTIC_USED'].fillna('')
            abx_list = df['PREVIOUS_ANTIBIOTIC_USED'].apply(
                lambda x: [i.strip() for i in str(x).split(';') if i.strip() != '']
            )
            abx_encoded = self.prev_abx_mlb.transform(abx_list)
            abx_df = pd.DataFrame(
                abx_encoded,
                columns=[f"PREV_ABX_{c}" for c in self.prev_abx_mlb.classes_],
                index=df.index
            )
            df = pd.concat([df, abx_df], axis=1)
            
        return df

    def predict(self, data):
        # Ensure input is a DataFrame
        input_df = pd.DataFrame([data]) if isinstance(data, dict) else pd.DataFrame(data)
        
        # Preprocess features
        X_processed = self._preprocess(input_df)

        # 1. Bacteria Type Prediction (Model 1)
        type_numeric = self.model_1.predict(X_processed)
        type_map = {0: 'Gram Negative', 1: 'Gram Positive'}
        type_labels = [type_map[p] for p in type_numeric]

        # Inject Model 1 output as a feature for Models 2 & 3
        X_processed['TYPE_OF_BACTERIA_ENC'] = type_numeric

        # 2. Resistance Prediction (Model 2)
        res_binary = self.model_2.predict(X_processed)
        res_labels = self.mlb_2.inverse_transform(res_binary)

        # 3. Sensitivity Prediction (Model 3)
        sens_binary = self.model_3.predict(X_processed)
        sens_labels = self.mlb_3.inverse_transform(sens_binary)

        # Build final response
        results = []
        for i in range(len(input_df)):
            results.append({
                "patient_index": i,
                "bacteria_type_prediction": type_labels[i],
                "predicted_resistant_antibiotics": list(res_labels[i]),
                "predicted_sensitive_antibiotics": list(sens_labels[i])
            })
        return results
            

# ==========================================
# TEST CASE
# ==========================================
if __name__ == "__main__":
    # 1. Initialize the engine (ensure .pkl files are in the same folder)
    engine = BacteriaInferenceEngine()

    # 2. Sample Data (Matching your provided CSV structure)
    test_patient = {
        "AGE": 52,
        "GENDER": "Male",
        "DEPARTMENT": "Urology",
        "CHIEF_COMPLAINTS": "Fever;Flank pain;Dysuria",
        "COMORBIDITIES": "Diabetes",
        "RISKFACTORS": "Catheterization",
        "SURGICAL_HISTORY": "",
        "SOCIAL_HISTORY": "Non smoker",
        "DIAGNOSIS": "Acute pyelonephritis",
        "CLASSIFICATION_OF_UTI": "Complicated",
        "TYPE_OF_UTI": "Acute",
        "SITE_OF_INFECTION": "Upper UTI",
        "TYPE_OF_SAMPLE": "Urine",
        "PREVIOUS_ANTIBIOTIC_USED": "Ciprofloxacin",
        "CBP_LYMPHOCYTES": 24,
        "WBC": 18200,
        "POLYMORPHS": 78,
        "CRP": 65,
        "RFT_SERUM_CREATININE": 2.1,
        "SERUM_URIC_ACID": 6.2,
        "BLOOD_UREA": 48,
        "CUE_PUS_CELLS": 28,
        "EPITHELIAL_CELLS": 6,
        "PROTEINS": "Positive",
        "RBC": 6
    }

    # 3. Run Inference
    print("\nRunning test inference...")
    try:
        output = engine.predict(test_patient)
        print("\n--- INFERENCE SUCCESSFUL ---")
        print(json.dumps(output, indent=4))
    except Exception as e:
        print(f"\n--- INFERENCE FAILED ---")
        import traceback
        traceback.print_exc()