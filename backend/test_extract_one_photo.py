import os
import io
import pdfplumber
from PIL import Image
import pypdf

filepath = os.path.join('nominal_roll', '2026 Nominal list-Business Studies, Accountancy, Economics,Computer Applications 39.pdf')

# Check pypdf image extraction or pdfplumber image extraction
reader = pypdf.PdfReader(filepath)
p0 = reader.pages[0]
print("pypdf p0 images count:", len(p0.images))
for i, img in enumerate(p0.images):
    print(f"  pypdf img {i}: name={img.name}, bytes_len={len(img.data)}")

# Save one image to test
os.makedirs('student_photos', exist_ok=True)
if p0.images:
    test_out = os.path.join('student_photos', 'test_photo_0.jpg')
    with open(test_out, 'wb') as f:
        f.write(p0.images[0].data)
    print("Saved test photo to:", test_out)
    
    # Check image dimensions
    im = Image.open(test_out)
    print("Image size:", im.size, "format:", im.format, "mode:", im.mode)
