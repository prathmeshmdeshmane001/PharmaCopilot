import os
import io
import docx
from pypdf import PdfWriter

os.makedirs("sample_data", exist_ok=True)

# 1. Sample TXT
txt_content = """HOSPITAL PHARMACOVIGILANCE INCIDENT REPORT
Facility: St. Jude Memorial Hospital Pharmacy
Date: 2026-03-10

Product Name: Epinephrine Injection
Strength: 1 mg/mL, USP
Batch / Lot Number: B24017
Manufacturing Date: 2025-10-15
Expiry Date: 2027-10-14
Affected Quantity: 50 vials

Defect Description:
During morning stock unpackaging in the Emergency Department pharmacy, staff observed liquid leakage around the aluminum crimp seal and rubber stopper in 50 glass vials. Immediate quarantine of the affected tray was initiated.
"""
with open("sample_data/sample_complaint.txt", "w", encoding="utf-8") as f:
    f.write(txt_content)

# 2. Sample DOCX
doc = docx.Document()
doc.add_heading("Customer Quality Defect Report", 0)
doc.add_paragraph("Customer Name: MetroHealth Specialty Clinic")
doc.add_paragraph("Product: Metformin Hydrochloride")
doc.add_paragraph("Dosage: 500 mg Tablets")
doc.add_paragraph("Batch Number: M9012")
doc.add_paragraph("Manufacturing Date: 2025-06-01")
doc.add_paragraph("Expiry Date: 2028-05-31")
doc.add_paragraph("Quantity Affected: 120 bottles")
doc.add_paragraph("Defect Type: Packaging / Closure Defect")
doc.add_paragraph("Detailed Description: Clinic received 120 bottles missing tamper-evident induction seals beneath the child-resistant closure. Bottles were segregated in quarantine.")
doc.save("sample_data/sample_packaging_defect.docx")

# 3. Sample EML
eml_content = """From: quality.assurance@citygeneralhospital.org
To: complaints@pharmaco.com
Subject: Urgent Notice: Foreign particulate in Normal Saline Lot NS4401
Date: Wed, 11 Mar 2026 14:15:00 -0400
Content-Type: text/plain; charset=utf-8

Customer: City General Hospital Infusion Center
Product Name: Normal Saline 0.9%
Product Grade: USP Infusion
Batch / Lot Number: NS4401
Quantity Affected: 15 bags
Defect: Foreign Particulate Matter

Dear Quality Assurance Team,
During pre-administration visual inspection, nursing staff identified visible black floating specks suspended in 15 infusion bags from Lot NS4401. All units from this lot have been quarantined immediately.
"""
with open("sample_data/sample_email_complaint.eml", "w", encoding="utf-8") as f:
    f.write(eml_content)

# 4. Sample PDF using pypdf
# In pypdf, we can create a PDF with a blank page and add annotations or metadata, or create a simple standard PDF stream
pdf_writer = PdfWriter()
pdf_writer.add_blank_page(width=612, height=792)
# To embed extractable text in PDF without external reportlab, we can write a raw PDF text stream
pdf_raw = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>
endobj
4 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
5 0 obj
<< /Length 450 >>
stream
BT
/F1 12 Tf
50 720 Td
(PHARMACEUTICAL COMPLAINT INTAKE DOSSIER) Tj
0 -25 Td
(Customer: Mercy Health System) Tj
0 -20 Td
(Product: Epinephrine Injection 1 mg/mL, USP) Tj
0 -20 Td
(Batch Number: B24017) Tj
0 -20 Td
(Manufacturing Date: 2025-10-15) Tj
0 -20 Td
(Expiry Date: 2027-10-14) Tj
0 -20 Td
(Quantity Affected: 50 vials) Tj
0 -20 Td
(Defect: Container Closure Leakage around rubber stopper) Tj
0 -20 Td
(Description: Leaking vials identified upon opening shipment carton.) Tj
ET
endstream
endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000227 00000 n 
0000000302 00000 n 
trailer
<< /Size 6 /Root 1 0 R >>
startxref
805
%%EOF"""

with open("sample_data/sample_complaint_letter.pdf", "wb") as f:
    f.write(pdf_raw)

print("Generated sample documents successfully.")
