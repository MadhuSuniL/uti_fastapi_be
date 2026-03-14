import io
import base64
import re
from datetime import datetime

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.colors import HexColor

class ReportService:
    def __init__(self):
        # --------------------------------------------------
        # PREMIUM COLOR PALETTE
        # --------------------------------------------------
        self.primary_color = HexColor("#0F7C95")  # Classic Pantone Blue (Professional)
        self.secondary_color = HexColor("#F8FAFC") # Ultra-light Slate for soft backgrounds
        self.border_color = HexColor("#E2E8F0")   # Soft border gray
        self.text_color = HexColor("#1E293B")     # Deep Slate for high readability
        self.muted_text = HexColor("#64748B")     # Muted gray for secondary info
        self.accent_red = HexColor("#FEF2F2")     # Soft Red 
        self.text_red = HexColor("#991B1B")       # Deep Red for warnings
        self.accent_green = HexColor("#F0FDF4")   # Soft Green
        self.text_green = HexColor("#065F46")     # Deep Green for positive indicators

        # Setup Styles
        styles = getSampleStyleSheet()
        self.styles = styles
        
        # Custom Typography
        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=self.primary_color,
            spaceAfter=5,
            fontName="Helvetica-Bold"
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=HexColor("#0F172A"),
            spaceBefore=18,
            spaceAfter=12,
            fontName="Helvetica-Bold",
            borderPadding=6,
            borderWidth=0,
            borderWidthBottom=1.5,
            borderColor=self.primary_color
        ))
        
        self.styles.add(ParagraphStyle(
            name='TableText',
            parent=styles['Normal'],
            fontSize=10,
            textColor=self.text_color,
            leading=14
        ))

        self.styles.add(ParagraphStyle(
            name='CustomBodyText',
            parent=styles['Normal'],
            fontSize=10,
            textColor=self.text_color,
            leading=16, # Increased leading for better readability
            spaceAfter=0
        ))

    
    
    def _normalize_the_results(self, results: dict):
        """
        Normalize all dictionary keys to lowercase recursively.
        """

        if isinstance(results, dict):
            return {
                key.lower(): self._normalize_the_results(value)
                for key, value in results.items()
            }

        elif isinstance(results, list):
            return [self._normalize_the_results(item) for item in results]

        else:
            return results
            
    # --------------------------------------------------
    # UTILITY: SANITIZE TEXT (Fixes the Black Squares)
    # --------------------------------------------------
    def _sanitize_text(self, text: str) -> str:
        """Removes special unicode characters that break standard ReportLab fonts"""
        if not isinstance(text, str):
            return str(text)
        
        # Replace non-breaking hyphens, en-dashes, em-dashes with standard hyphen
        text = text.replace('\u2011', '-').replace('\u2013', '-').replace('\u2014', '-')
        # Replace fancy quotes with standard quotes
        text = text.replace('\u2018', "'").replace('\u2019', "'")
        text = text.replace('\u201c', '"').replace('\u201d', '"')
        # Replace non-breaking spaces
        text = text.replace('\u00a0', ' ')
        
        return text

    def _parse_markdown_to_paragraphs(self, text: str) -> list:
        """Convert markdown text into a list of spaced ReportLab Paragraphs"""
        text = self._sanitize_text(text)
        if not text:
            return []
            
        elements = []
        blocks = text.split('\n\n')
        
        for block in blocks:
            # Convert Bold and Italic
            block = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', block)
            block = re.sub(r'(?<!\w)\*(.*?)\*(?!\w)', r'<i>\1</i>', block)
            
            lines = block.split('\n')
            formatted_lines = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                if line.startswith('- '):
                    line = "&bull; " + line[2:]
                formatted_lines.append(line)
                
            if formatted_lines:
                paragraph_text = "<br/>".join(formatted_lines)
                elements.append(Paragraph(paragraph_text, self.styles["CustomBodyText"]))
                elements.append(Spacer(1, 8)) 
                
        return elements

    def generate_report(self, data: dict) -> str:
        """Generate PDF report and return base64 encoded data"""
        data = self._normalize_the_results(data)
        buffer = io.BytesIO()

        # Premium Margin Setup
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=40,
            leftMargin=40,
            topMargin=50,
            bottomMargin=60 
        )

        elements = []
        
        elements += self._build_header()
        elements += self._build_patient_section(data)
        elements += self._build_clinical_section(data)
        elements += self._build_lab_section(data)
        elements += self._build_prediction_section(data)
        elements += self._build_antibiotic_section(data)
        elements += self._build_recommendation_section(data)
        elements += self._build_history_section(data)
        elements += self._build_summary_section(data)

        doc.build(
            elements, 
            onFirstPage=self._add_footer, 
            onLaterPages=self._add_footer
        )

        pdf = buffer.getvalue()
        buffer.close()

        return base64.b64encode(pdf).decode()

    # --------------------------------------------------
    # PREMIUM FOOTER CALLBACK 
    # --------------------------------------------------
    def _add_footer(self, canvas, doc):
        canvas.saveState()
        
        # Top Accent Line for the whole page (adds a premium letterhead feel)
        canvas.setStrokeColor(self.primary_color)
        canvas.setLineWidth(3)
        canvas.line(0, A4[1], A4[0], A4[1])

        # Bottom Footer
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(self.muted_text)
        
        footer_text = f"AI-Powered UTI Antibiotic Recommendation System | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        page_num = f"Page {doc.page}"
        
        # Subtle footer divider
        canvas.setStrokeColor(self.border_color)
        canvas.setLineWidth(1)
        canvas.line(40, 40, A4[0] - 40, 40)
        
        # Draw elements
        canvas.drawString(40, 25, footer_text)
        canvas.drawRightString(A4[0] - 40, 25, page_num)
        
        canvas.restoreState()

    # --------------------------------------------------
    # FIRST PAGE HEADER 
    # --------------------------------------------------
    def _build_header(self):
        title = Paragraph("AI-Powered UTI Antibiotic System", self.styles["ReportTitle"])
        subtitle = Paragraph(
            f"<font color='{self.muted_text}'><b>ANALYSIS REPORT &bull; ACADEMIC RESEARCH DOCUMENT</b></font>", 
            self.styles["CustomBodyText"]
        )
        return [title, subtitle, Spacer(3, 25)]

    # --------------------------------------------------
    # PATIENT DETAILS
    # --------------------------------------------------
    def _build_patient_section(self, data):
        patient = data.get("patient_details", {})
        
        table_data = [
            [Paragraph("<b>Age / Gender</b>", self.styles['TableText']), Paragraph(self._sanitize_text(f"{patient.get('age', 'N/A')} / {patient.get('gender', 'N/A')}"), self.styles['TableText'])],
            [Paragraph("<b>Department</b>", self.styles['TableText']), Paragraph(self._sanitize_text(patient.get("department", "N/A")), self.styles['TableText'])],
            [Paragraph("<b>Diagnosis</b>", self.styles['TableText']), Paragraph(self._sanitize_text(patient.get("diagnosis", "N/A")), self.styles['TableText'])],
            [Paragraph("<b>UTI Classification</b>", self.styles['TableText']), Paragraph(self._sanitize_text(patient.get("classification_of_uti", "N/A")), self.styles['TableText'])],
            [Paragraph("<b>Sample Type</b>", self.styles['TableText']), Paragraph(self._sanitize_text(patient.get("type_of_sample", "N/A")), self.styles['TableText'])],
        ]

        table = Table(table_data, colWidths=[150, 360])
        table.setStyle(self._standard_table_style())

        title = Paragraph("Patient Demographics", self.styles["SectionHeader"])
        return [KeepTogether([title, table, Spacer(1, 15)])]

    # --------------------------------------------------
    # CLINICAL DETAILS
    # --------------------------------------------------
    def _build_clinical_section(self, data):
        patient = data.get("patient_details", {})
        text = f"""
        <b>Chief Complaints:</b> {patient.get('chief_complaints', 'N/A')} <br/>
        <b>Comorbidities:</b> {patient.get('comorbidities', 'None')} <br/>
        <b>Surgical History:</b> {patient.get('surgical_history', 'None')} <br/>
        <b>Social History:</b> {patient.get('social_history', 'None')}
        """
        title = Paragraph("Clinical Presentation", self.styles["SectionHeader"])
        paragraph = Paragraph(self._sanitize_text(text), self.styles["CustomBodyText"])
        return [KeepTogether([title, paragraph, Spacer(1, 15)])]

    # --------------------------------------------------
    # LAB RESULTS
    # --------------------------------------------------
    def _build_lab_section(self, data):
        patient_details = data.get("patient_details", {})
        lab_details = patient_details.get("lab_results", {})

        LAB_METADATA = {
            "cbp_lymphocytes": {"unit": "%", "range": "20 - 40"},
            "wbc": {"unit": "cells/µL", "range": "4000 - 11000"},
            "polymorphs": {"unit": "%", "range": "40 - 75"},
            "crp": {"unit": "mg/L", "range": "< 10"},
            "rft_serum_creatinine": {"unit": "mg/dL", "range": "0.6 - 1.3"},
            "serum_uric_acid": {"unit": "mg/dL", "range": "3.5 - 7.2"},
            "blood_urea": {"unit": "mg/dL", "range": "7 - 20"},
            "cue_pus_cells": {"unit": "/HPF", "range": "0 - 5"},
            "epithelial_cells": {"unit": "/HPF", "range": "0 - 5"},
            "proteins": {"unit": "", "range": "Negative"},
            "rbc": {"unit": "/HPF", "range": "0 - 3"},
        }

        labs = {
            key: patient_details.get(key, lab_details.get(key))
            for key in LAB_METADATA.keys()
        }

        table_data = [[
            Paragraph("<b>Test Name</b>", self.styles['TableText']),
            Paragraph("<b>Value</b>", self.styles['TableText']),
            Paragraph("<b>Unit</b>", self.styles['TableText']),
            Paragraph("<b>Normal Range</b>", self.styles['TableText'])
        ]]

        for k, v in labs.items():
            meta = LAB_METADATA.get(k, {})
            unit = meta.get("unit", "")
            normal_range = meta.get("range", "")

            clean_key = k.replace("_", " ").title()

            table_data.append([
                Paragraph(self._sanitize_text(clean_key), self.styles['TableText']),
                Paragraph(self._sanitize_text(str(v)), self.styles['TableText']),
                Paragraph(self._sanitize_text(unit), self.styles['TableText']),
                Paragraph(self._sanitize_text(normal_range), self.styles['TableText'])
            ])

        table = Table(table_data, colWidths=[180, 110, 100, 120])
        table.setStyle(self._header_table_style())

        title = Paragraph("Laboratory Results", self.styles["SectionHeader"])

        return [KeepTogether([title, table, Spacer(1, 15)])]

    # --------------------------------------------------
    # AI PREDICTION
    # --------------------------------------------------
    def _build_prediction_section(self, data):
        pred = data.get("predictions", {})

        org_name = self._sanitize_text(pred.get('organism_name_prediction', 'N/A'))
        bac_type = self._sanitize_text(pred.get("bacteria_type_prediction", "N/A"))

        table_data = [
            [Paragraph("<b>Predicted Organism</b>", self.styles['TableText']), 
             Paragraph(f"<font color='{self.primary_color}'><b>{org_name}</b></font>", self.styles['TableText'])],
            [Paragraph("<b>Bacteria Type</b>", self.styles['TableText']), 
             Paragraph(bac_type, self.styles['TableText'])],
        ]

        table = Table(table_data, colWidths=[150, 360])
        table.setStyle(self._standard_table_style())

        title = Paragraph("AI Pathogen Prediction", self.styles["SectionHeader"])
        return [KeepTogether([title, table, Spacer(1, 15)])]

    # --------------------------------------------------
    # ANTIBIOTIC PROFILE
    # --------------------------------------------------
    def _build_antibiotic_section(self, data):
        pred = data.get("predictions", {})
        resistant = self._sanitize_text(", ".join(pred.get("predicted_resistant_antibiotics", [])))
        sensitive = self._sanitize_text(", ".join(pred.get("predicted_sensitive_antibiotics", [])))

        table_data = [
            [Paragraph("<b>Predicted Sensitive</b>", self.styles['TableText']), Paragraph(f"<font color='{self.text_green}'><b>{sensitive}</b></font>", self.styles['TableText'])],
            [Paragraph("<b>Predicted Resistant</b>", self.styles['TableText']), Paragraph(f"<font color='{self.text_red}'><b>{resistant}</b></font>", self.styles['TableText'])]
        ]

        table = Table(table_data, colWidths=[150, 360])
        
        style = self._standard_table_style()
        style.add('BACKGROUND', (0, 0), (1, 0), self.accent_green)
        style.add('BACKGROUND', (0, 1), (1, 1), self.accent_red)
        table.setStyle(style)

        title = Paragraph("Antibiotic Susceptibility Profile", self.styles["SectionHeader"])
        return [KeepTogether([title, table, Spacer(1, 15)])]

    # --------------------------------------------------
    # RECOMMENDED THERAPY (Premium Cards)
    # --------------------------------------------------
    def _build_recommendation_section(self, data):
        recs = data.get("prescribed_antibiotics", {}).get("recommended", [])
        title = Paragraph("Recommended Therapy", self.styles["SectionHeader"])
        elements = [title]

        for r in recs:
            name = self._sanitize_text(r.get('name', 'Unknown'))
            dosage = self._sanitize_text(r.get('dosage', 'N/A'))
            precautions = self._sanitize_text(r.get('precautions', 'N/A'))
            explanation = self._sanitize_text(r.get('explanation', 'N/A'))

            text = f"""
            <b><font size=12 color='{self.primary_color}'>{name}</font></b><br/><br/>
            <b>Dosage:</b> {dosage}<br/><br/>
            <b>Precautions:</b> <font color='{self.text_red}'>{precautions}</font><br/><br/>
            <b>Rationale:</b> {explanation}
            """
            
            card_data = [[Paragraph(text, self.styles['CustomBodyText'])]]
            card = Table(card_data, colWidths=[510])
            
            # Premium "Ribbon" style card
            card.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), self.secondary_color),
                ('BOX', (0, 0), (-1, -1), 0.5, self.border_color),
                # Thick colored line on the left to make it pop
                ('LINEBEFORE', (0, 0), (0, -1), 3, self.primary_color), 
                ('TOPPADDING', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('LEFTPADDING', (0, 0), (-1, -1), 15),
                ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ]))
            
            elements.append(KeepTogether([card, Spacer(1, 12)]))

        return elements

    # --------------------------------------------------
    # ANTIBIOTIC HISTORY
    # --------------------------------------------------
    def _build_history_section(self, data):
        history = data.get("antibiotic_history", {})
        if not history: 
            return []
        
        title = Paragraph("Antibiotic Drug History", self.styles["SectionHeader"])
        elements = [title]

        for drug_name, details in history.items():
            if details.get("background") == "No information available":
                continue

            name = self._sanitize_text(drug_name.title())
            bg = self._sanitize_text(details.get('background', 'N/A'))
            usage = self._sanitize_text(details.get('common_usage', 'N/A'))
            mech = self._sanitize_text(details.get('mechanism_of_action', 'N/A'))
            historical_success = self._sanitize_text(details.get("historical_success", "N/A"))
            side_effects = self._sanitize_text(details.get("side_effects", "N/A"))
            resistance_notes = self._sanitize_text(details.get("resistance_notes", "N/A"))

            text = f"""
            <b><font color='{self.primary_color}'>{name}</font></b><br/><br/>
            <b>Background:</b> {bg}<br/>
            <b>Usage:</b> {usage}<br/>
            <b>Mechanism:</b> {mech}<br/>
            <b>Historical Success:</b> {historical_success}<br/>
            <b>Side Effects:</b> {side_effects}<br/>
            <b>Resistance Notes:</b> {resistance_notes}
            """
            elements.append(KeepTogether([Paragraph(text, self.styles["CustomBodyText"]), Spacer(1, 8)]))

        return elements

    # --------------------------------------------------
    # SUMMARY
    # --------------------------------------------------
    def _build_summary_section(self, data):
        title = Paragraph("Clinical Summary", self.styles["SectionHeader"])
        elements = [title, Spacer(1, 5)]
        
        raw_summary = data.get("summary", "")
        parsed_paragraphs = self._parse_markdown_to_paragraphs(raw_summary)
        
        elements.extend(parsed_paragraphs)
        return elements

    # --------------------------------------------------
    # TABLE STYLES
    # --------------------------------------------------
    def _standard_table_style(self):
        """Crisp, clean key-value pair table style"""
        return TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), self.secondary_color),
            ('TEXTCOLOR', (0, 0), (-1, -1), self.text_color),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, self.border_color),
            ('PADDING', (0, 0), (-1, -1), 10), # Added more breathing room
        ])

    def _header_table_style(self):
        """Table style with a top header row"""
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.primary_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, self.border_color),
            ('PADDING', (0, 0), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.secondary_color]),
        ])
if __name__ == "__main__":
    import json
    report_service = ReportService()
    
    # Example test harness
    try:
        with open("sample_input.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            
        pdf_base64 = report_service.generate_report(data)

        with open("premium_report.pdf", "wb") as f:
            f.write(base64.b64decode(pdf_base64))

        print("Premium Report Generated: premium_report.pdf")
    except FileNotFoundError:
        print("sample_input.json not found. Please ensure the file is in the same directory.")