import os
import json
import requests
from tqdm import tqdm
from datetime import datetime

# ----------------------------------------------------
# CONFIG
# ----------------------------------------------------

BASE_URL = "http://localhost:8000"

GET_PATIENTS_API = f"{BASE_URL}/patient_records"
PREDICT_API = f"{BASE_URL}/predict"
REPORT_API = f"{BASE_URL}/generate_report"

OUTPUT_DIR = "generated_reports"
RESULT_JSON = "patient_results.json"

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ----------------------------------------------------
# HELPERS
# ----------------------------------------------------

def load_existing_results():
    """Load already processed results (resume support)."""
    if os.path.exists(RESULT_JSON):
        with open(RESULT_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_result(result):
    """Append result safely after every patient."""
    if os.path.exists(RESULT_JSON):
        with open(RESULT_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = []

    data.append(result)

    with open(RESULT_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def generate_patient_id(index):
    """Generate hospital style patient ID"""
    return f"P{index+1:04d}"


def download_pdf(pdf_bytes, patient_id):
    """Save PDF report using Patient ID"""
    filename = f"{patient_id}.pdf"
    filepath = os.path.join(OUTPUT_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(pdf_bytes)

    return filepath


# ----------------------------------------------------
# MAIN PIPELINE
# ----------------------------------------------------

def main():

    print("Fetching patient records...")

    response = requests.get(GET_PATIENTS_API)
    response.raise_for_status()

    patients = response.json()

    print(f"Total patients received: {len(patients)}")

    processed_results = load_existing_results()
    processed_count = len(processed_results)

    print(f"Already processed: {processed_count}")

    patients = patients[processed_count:]  # resume support

    for idx, patient in enumerate(tqdm(patients, desc="Processing Patients")):
        try:

            global_index = processed_count + idx
            patient_id = generate_patient_id(global_index)

            # ------------------------------------------------
            # 1. Prediction
            # ------------------------------------------------

            pred_response = requests.post(
                PREDICT_API,
                json=patient,
                timeout=600
            )

            pred_response.raise_for_status()
            prediction_result = pred_response.json()

            # ------------------------------------------------
            # 2. Generate Report
            # ------------------------------------------------

            report_response = requests.post(
                REPORT_API,
                json=prediction_result,
                timeout=600
            )

            report_response.raise_for_status()

            pdf_path = download_pdf(
                report_response.content,
                patient_id
            )

            # ------------------------------------------------
            # 3. Save tracking result
            # ------------------------------------------------

            record = {
                "patient_id": patient_id,
                "timestamp": str(datetime.now()),
                "input": patient,
                "output": prediction_result,
                "pdf_path": pdf_path,
                "status": "success"
            }

            save_result(record)

        except Exception as e:

            global_index = processed_count + idx
            patient_id = generate_patient_id(global_index)

            error_record = {
                "patient_id": patient_id,
                "timestamp": str(datetime.now()),
                "input": patient,
                "error": str(e),
                "status": "failed"
            }

            save_result(error_record)

            print(f"\nError processing {patient_id}: {e}")


# ----------------------------------------------------

if __name__ == "__main__":
    main()
    # data = json.load(open("patient_results.json"))
    # data = filter(lambda x: x["status"] == "success", data)
    # data = sorted(data, key=lambda x : x["patient_id"])

    # for obj in data:
    #     obj["pdf_report"] = obj["pdf_path"].split("\\")[-1]
    #     obj.pop("pdf_path")

    # json.dump(data, open("daata.json", "w"), indent=4)