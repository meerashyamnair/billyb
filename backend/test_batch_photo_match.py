import pdfplumber
import os
import io
from PIL import Image

output_dir = 'student_photos'
os.makedirs(output_dir, exist_ok=True)

pdf_files = [f for f in os.listdir('nominal_roll') if f.endswith('.pdf')]
total_photos_extracted = 0

for filename in pdf_files:
    filepath = os.path.join('nominal_roll', filename)
    with pdfplumber.open(filepath) as pdf:
        active_header = None
        doc_photo_count = 0
        for p_idx, page in enumerate(pdf.pages):
            # 1. Extract table rows on page
            tables = page.extract_tables()
            page_student_rows = []
            for table in tables:
                if not table:
                    continue
                first_row = [c or '' for c in table[0]]
                has_header = any('Name' in c or 'Sl' in c for c in first_row)
                if has_header:
                    active_header = first_row
                    data_rows = table[1:]
                else:
                    data_rows = table
                for r in data_rows:
                    if any(r):
                        page_student_rows.append(r)
            
            # 2. Extract and sort images on page
            page_images = sorted(page.images, key=lambda im: im['top'])
            # Filter student photos (width between 30 and 70, height between 40 and 80)
            student_photos = [im for im in page_images if 30 <= im['width'] <= 70 and 40 <= im['height'] <= 80]
            
            # Check matching
            print(f"{filename} Page {p_idx+1}: {len(page_student_rows)} student rows, {len(student_photos)} photos")
            for i in range(min(len(page_student_rows), len(student_photos))):
                im = student_photos[i]
                stream = im.get('stream')
                raw_bytes = stream.get_data()
                doc_photo_count += 1
                total_photos_extracted += 1
                
        print(f"-> Extracted {doc_photo_count} photos from {filename}")

print(f"TOTAL PHOTOS EXTRACTED: {total_photos_extracted}")
