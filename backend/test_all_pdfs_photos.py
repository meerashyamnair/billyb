import pdfplumber
import os

pdf_files = [f for f in os.listdir('nominal_roll') if f.endswith('.pdf')]
for f in pdf_files:
    filepath = os.path.join('nominal_roll', f)
    with pdfplumber.open(filepath) as pdf:
        total_imgs = sum(len(p.images) for p in pdf.pages)
        print(f"{f}: {len(pdf.pages)} pages, {total_imgs} embedded images")
