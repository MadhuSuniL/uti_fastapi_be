import json
import pandas as pd

INPUT_FILE = "patient_results.json"
OUTPUT_FILE = "UTI_EVALUATION_REPORT.xlsx"


# --------------------------------------------------
# Utility Functions
# --------------------------------------------------

def split_antibiotics(text):
    if not text:
        return set()
    return set([x.strip().lower() for x in text.split(";")])


def similarity_percentage(original, predicted):

    orig_set = split_antibiotics(original)
    pred_set = set([x.strip().lower() for x in predicted])

    if len(orig_set) == 0:
        return 0

    match = len(orig_set.intersection(pred_set))

    return round((match / len(orig_set)) * 100, 2)


def organism_accuracy(original, predicted):

    if not original or not predicted:
        return 0

    if original.strip().lower() == predicted.strip().lower():
        return 100

    return 0


# --------------------------------------------------
# Load JSON
# --------------------------------------------------

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

rows = []

# --------------------------------------------------
# Process Patients
# --------------------------------------------------

for idx, item in enumerate(data):

    if item["status"] != "success":
        continue

    inp = item["input"]
    out = item["output"]

    preds = out["predictions"]

    row = {}

    # --------------------------------------------------
    # Patient ID
    # --------------------------------------------------

    row["PATIENT_ID"] = f"P{idx+1:04d}"

    # --------------------------------------------------
    # Input Columns (except target columns)
    # --------------------------------------------------

    for k, v in inp.items():

        if k in ["ORGANISM_NAME", "RESISTANT", "SENSITIVE"]:
            continue

        row[k.upper()] = v

    # --------------------------------------------------
    # Original Target Columns
    # --------------------------------------------------

    original_organism = inp.get("ORGANISM_NAME")
    original_resistant = inp.get("RESISTANT")
    original_sensitive = inp.get("SENSITIVE")

    row["ORIGINAL_ORGANISM_NAME"] = original_organism
    row["ORIGINAL_RESISTANT_ANTIBIOTICS"] = original_resistant
    row["ORIGINAL_SENSITIVE_ANTIBIOTICS"] = original_sensitive

    # --------------------------------------------------
    # Predictions
    # --------------------------------------------------

    predicted_organism = preds.get("organism_name_prediction")
    predicted_type = preds.get("bacteria_type_prediction")

    predicted_resistant = preds.get("predicted_resistant_antibiotics", [])
    predicted_sensitive = preds.get("predicted_sensitive_antibiotics", [])

    row["PREDICTED_ORGANISM_NAME"] = predicted_organism
    row["PREDICTED_BACTERIA_TYPE"] = predicted_type
    row["PREDICTED_RESISTANT_ANTIBIOTICS"] = ";".join(predicted_resistant)
    row["PREDICTED_SENSITIVE_ANTIBIOTICS"] = ";".join(predicted_sensitive)

    # --------------------------------------------------
    # Accuracy Calculations
    # --------------------------------------------------

    bacteria_acc = organism_accuracy(original_organism, predicted_organism)

    resistant_acc = similarity_percentage(
        original_resistant,
        predicted_resistant
    )

    sensitive_acc = similarity_percentage(
        original_sensitive,
        predicted_sensitive
    )

    overall_acc = round(
        (bacteria_acc + resistant_acc + sensitive_acc) / 3,
        2
    )

    row["BACTERIA_ACCURACY_PERCENT"] = bacteria_acc
    row["RESISTANT_MATCH_PERCENT"] = resistant_acc
    row["SENSITIVE_MATCH_PERCENT"] = sensitive_acc
    row["OVERALL_ACCURACY_PERCENT"] = overall_acc

    # --------------------------------------------------
    # Recommended Antibiotics
    # --------------------------------------------------

    recommended = out["prescribed_antibiotics"]["recommended"]

    names = [x["name"] for x in recommended]

    row["RECOMMENDED_ANTIBIOTICS"] = ";".join(names)

    rows.append(row)


# --------------------------------------------------
# Create Excel
# --------------------------------------------------

df = pd.DataFrame(rows)
df.to_excel(OUTPUT_FILE, index=False)

print("Excel report generated:", OUTPUT_FILE)