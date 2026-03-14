import requests
import pandas as pd


# --------------------------------------------------
# API CONFIG
# --------------------------------------------------

API_URL = "http://localhost:8000/patient_records"


# --------------------------------------------------
# FETCH DATA FROM API
# --------------------------------------------------

response = requests.get(API_URL)

if response.status_code != 200:
    raise Exception(f"API request failed: {response.status_code}")

patients = response.json()


# --------------------------------------------------
# ENSURE DATA IS LIST
# --------------------------------------------------

if isinstance(patients, dict):
    patients = [patients]


# --------------------------------------------------
# ADD PATIENT ID (P0001 FORMAT)
# --------------------------------------------------

for i, patient in enumerate(patients, start=1):
    patient["PATIENT_ID"] = f"P{i:04d}"


# --------------------------------------------------
# CONVERT TO DATAFRAME
# --------------------------------------------------

df = pd.DataFrame(patients)


# --------------------------------------------------
# MOVE PATIENT_ID TO FIRST COLUMN
# --------------------------------------------------

cols = df.columns.tolist()

cols.insert(0, cols.pop(cols.index("PATIENT_ID")))

df = df[cols]


# --------------------------------------------------
# SAVE EXCEL
# --------------------------------------------------

output_file = "patient_dataset.xlsx"

df.to_excel(output_file, index=False)


print("Excel file generated successfully:", output_file)