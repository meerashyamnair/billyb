import pdfplumber
import pypdf
import os
from PIL import Image
import io

filepath = os.path.join('nominal_roll', '2026 Nominal list-Business Studies, Accountancy, Economics,Computer Applications 39.pdf')

# Test method 1: Using pypdf's page.images
reader = pypdf.PdfReader(filepath)
for p_idx in range(min(2, len(reader.pages))):
    p = reader.pages[p_idx]
    print(f"Page {p_idx+1} pypdf images count: {len(p.images)}")
    for img_file in p.images:
        print(f"   Image name: {img_file.name}, length: {len(img_file.data)}")

# Test method 2: Check matching with pdfplumber table row
with pdfplumber.open(filepath) as pdf:
    p0 = pdf.pages[0]
    sorted_imgs = sorted(p0.images, key=lambda im: im['top'])
    for i, im in enumerate(sorted_imgs):
        stream = im.get('stream')
        raw_data = stream.get_data()
        print(f"pdfplumber img {i} ({im.get('name')}): raw_data len: {len(raw_data)}")
        img = Image.open(io.BytesIO(raw_data))
        print(f"   Parsed with PIL: size={img.size}, format={img.format}")
