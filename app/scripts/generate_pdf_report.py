import json
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch


# ---------------------------------------------------
# COLOR PALETTE
# ---------------------------------------------------

primary_color = HexColor("#0F7C95")
secondary_color = HexColor("#F8FAFC")
border_color = HexColor("#E2E8F0")
text_color = HexColor("#1E293B")
muted_text = HexColor("#64748B")

accent_red = HexColor("#FEF2F2")
text_red = HexColor("#991B1B")

accent_green = HexColor("#F0FDF4")
text_green = HexColor("#065F46")


# ---------------------------------------------------
# LOAD JSON DATA
# ---------------------------------------------------

with open("patient_results.json", "r", encoding="utf-8") as f:
    patients = json.load(f)


# ---------------------------------------------------
# PDF SETUP
# ---------------------------------------------------

doc = SimpleDocTemplate(
    "UTI_AI_SYSTEM_EVALUATION_REPORT.pdf",
    pagesize=A4,
    rightMargin=40,
    leftMargin=40,
    topMargin=40,
    bottomMargin=40
)

styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    "Title",
    parent=styles["Heading1"],
    textColor=primary_color,
    alignment=1
)

section_style = ParagraphStyle(
    "Section",
    parent=styles["Heading3"],
    textColor=primary_color
)

text_style = ParagraphStyle(
    "Text",
    parent=styles["Normal"],
    textColor=text_color
)


story = []


# ---------------------------------------------------
# HELPER FUNCTION FOR TABLE STYLE
# ---------------------------------------------------

def styled_table(data):

    table = Table(data, colWidths=[2.5 * inch, 4 * inch])

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), secondary_color),
        ("GRID", (0, 0), (-1, -1), 0.5, border_color),
        ("TEXTCOLOR", (0, 0), (-1, -1), text_color),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))

    return table


# ---------------------------------------------------
# GENERATE REPORT
# ---------------------------------------------------

for patient in patients:

    if patient.get("status") != "success":
        continue

    inp = patient.get("input", {})
    out = patient.get("output", {})
    preds = out.get("predictions", {})

    patient_id = patient.get("patient_id", "Unknown")

    story.append(Paragraph("UTI AI Sytem Evaluation Report", title_style))
    story.append(Spacer(1, 20))

    story.append(Paragraph(f"<b>Patient ID:</b> {patient_id}", text_style))
    story.append(Spacer(1, 20))


    # ---------------------------------------------------
    # PATIENT INFORMATION
    # ---------------------------------------------------

    story.append(Paragraph("PATIENT INFORMATION", section_style))
    story.append(Spacer(1, 10))

    patient_info = [
        ["Age", inp.get("AGE")],
        ["Gender", inp.get("GENDER")],
        ["Department", inp.get("DEPARTMENT")],
        ["Diagnosis", inp.get("DIAGNOSIS")],
        ["Comorbidities", inp.get("COMORBIDITIES")],
        ["Risk Factors", inp.get("RISKFACTORS")],
        ["Surgical History", inp.get("SURGICAL_HISTORY")],
        ["Social History", inp.get("SOCIAL_HISTORY")],
    ]

    story.append(styled_table(patient_info))
    story.append(Spacer(1, 20))


    # ---------------------------------------------------
    # PREVIOUS ANTIBIOTICS
    # ---------------------------------------------------

    story.append(Paragraph("PREVIOUS ANTIBIOTICS USED", section_style))
    story.append(Spacer(1, 10))

    prev_ab = inp.get("PREVIOUS_ANTIBIOTIC_USED", "None")

    story.append(styled_table([["Previous Antibiotic", prev_ab]]))
    story.append(Spacer(1, 20))


    # ---------------------------------------------------
    # LAB RESULTS
    # ---------------------------------------------------

    story.append(Paragraph("LAB RESULTS", section_style))
    story.append(Spacer(1, 10))

    lab_results = [
        ["WBC", inp.get("WBC")],
        ["CBP Lymphocytes", inp.get("CBP_LYMPHOCYTES")],
        ["Polymorphs", inp.get("POLYMORPHS")],
        ["CRP", inp.get("CRP")],
        ["Serum Creatinine", inp.get("RFT_SERUM_CREATININE")],
        ["Serum Uric Acid", inp.get("SERUM_URIC_ACID")],
        ["Blood Urea", inp.get("BLOOD_UREA")],
        ["Pus Cells", inp.get("CUE_PUS_CELLS")],
        ["Epithelial Cells", inp.get("EPITHELIAL_CELLS")],
        ["Proteins", inp.get("PROTEINS")],
        ["RBC", inp.get("RBC")],
    ]

    story.append(styled_table(lab_results))
    story.append(Spacer(1, 20))


    # ---------------------------------------------------
    # ORGANISM PREDICTION
    # ---------------------------------------------------

    story.append(Paragraph("ORGANISM PREDICTION", section_style))
    story.append(Spacer(1, 10))

    organism_table = [
        ["Actual Organism", inp.get("ORGANISM_NAME")],
        ["Predicted Organism", preds.get("organism_name_prediction")]
    ]

    story.append(styled_table(organism_table))
    story.append(Spacer(1, 20))


    # ---------------------------------------------------
    # RESISTANCE COMPARISON
    # ---------------------------------------------------

    story.append(Paragraph("ANTIBIOTIC RESISTANCE COMPARISON", section_style))
    story.append(Spacer(1, 10))

    resistant_pred = "; ".join(preds.get("predicted_resistant_antibiotics", []))

    resistance_table = [
        ["Original Resistant", inp.get("RESISTANT")],
        ["Predicted Resistant", resistant_pred],
    ]

    story.append(styled_table(resistance_table))
    story.append(Spacer(1, 20))


    # ---------------------------------------------------
    # SENSITIVITY COMPARISON
    # ---------------------------------------------------

    story.append(Paragraph("ANTIBIOTIC SENSITIVITY COMPARISON", section_style))
    story.append(Spacer(1, 10))

    sensitive_pred = "; ".join(preds.get("predicted_sensitive_antibiotics", []))

    sensitivity_table = [
        ["Original Sensitive", inp.get("SENSITIVE")],
        ["Predicted Sensitive", sensitive_pred],
    ]

    story.append(styled_table(sensitivity_table))
    story.append(Spacer(1, 20))


    # ---------------------------------------------------
    # RECOMMENDED ANTIBIOTICS
    # ---------------------------------------------------

    story.append(Paragraph("RECOMMENDED ANTIBIOTICS", section_style))
    story.append(Spacer(1, 10))

    recommended = out.get("prescribed_antibiotics", {}).get("recommended", [])

    rec_data = []

    for r in recommended:
        rec_data.append(["Antibiotic", r.get("name")])

    if not rec_data:
        rec_data = [["Antibiotic", "None"]]

    story.append(styled_table(rec_data))
    story.append(Spacer(1, 20))


    # ---------------------------------------------------
    # SYSTEM ACCURACY EVALUATION
    # ---------------------------------------------------

    story.append(Paragraph("SYSTEM ACCURACY EVALUATION", section_style))
    story.append(Spacer(1, 10))


    # Organism Accuracy
    actual_org = inp.get("ORGANISM_NAME")
    pred_org = preds.get("organism_name_prediction")

    organism_accuracy = 1 if actual_org == pred_org else 0


    # Resistant Accuracy
    actual_res = set([x.strip() for x in str(inp.get("RESISTANT", "")).split(";") if x])
    pred_res = set(preds.get("predicted_resistant_antibiotics", []))

    resistant_accuracy = (
        len(actual_res & pred_res) / len(actual_res) if len(actual_res) else 0
    )


    # Sensitive Accuracy
    actual_sens = set([x.strip() for x in str(inp.get("SENSITIVE", "")).split(";") if x])
    pred_sens = set(preds.get("predicted_sensitive_antibiotics", []))

    sensitive_accuracy = (
        len(actual_sens & pred_sens) / len(actual_sens) if len(actual_sens) else 0
    )


    # Overall Accuracy
    overall_accuracy = (
        organism_accuracy + resistant_accuracy + sensitive_accuracy
    ) / 3


    accuracy_table = [
        ["Metric", "Accuracy"],
        ["Organism Prediction", f"{organism_accuracy*100:.2f}%"],
        ["Resistant Antibiotics", f"{resistant_accuracy*100:.2f}%"],
        ["Sensitive Antibiotics", f"{sensitive_accuracy*100:.2f}%"],
        ["Overall Sytem Accuracy", f"{overall_accuracy*100:.2f}%"],
    ]

    acc_table = Table(accuracy_table, colWidths=[3 * inch, 3 * inch])

    acc_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), secondary_color),
        ("GRID", (0, 0), (-1, -1), 0.5, border_color),
        ("TEXTCOLOR", (0, 0), (-1, -1), text_color),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
    ]))

    story.append(acc_table)
    story.append(Spacer(1, 20))


    # ---------------------------------------------------
    # PAGE BREAK
    # ---------------------------------------------------

    story.append(PageBreak())


# ---------------------------------------------------
# BUILD PDF
# ---------------------------------------------------

doc.build(story)

print("PDF report generated successfully.")