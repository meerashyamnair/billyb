import pdfplumber
import os

pdf_files = [f for f in os.listdir('nominal_roll') if f.endswith('.pdf')]
for filename in pdf_files[:2]:
    filepath = os.path.join('nominal_roll', filename)
    print("=" * 60)
    print("Checking file:", filename)
    with pdfplumber.open(filepath) as pdf:
        print("Total pages:", len(pdf.pages))
        for p_idx in range(min(2, len(pdf.pages))):
            page = pdf.pages[p_idx]
            print(f"--- Page {p_idx+1} ---")
            print("Images on page:", len(page.images))
            for i, img in enumerate(page.images):
                print(f"  Img {i}: x0={img['x0']:.1f}, top={img['top']:.1f}, x1={img['x1']:.1f}, bottom={img['bottom']:.1f}, w={img['width']:.1f}, h={img['height']:.1f}, stream={img.get('stream') is not None}")
