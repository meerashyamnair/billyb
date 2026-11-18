import pdfplumber
import pypdf
import os

filepath = os.path.join('nominal_roll', '2026 Nominal list-Business Studies, Accountancy, Economics,Computer Applications 39.pdf')

with pdfplumber.open(filepath) as pdf:
    for p_idx in range(len(pdf.pages)):
        page = pdf.pages[p_idx]
        images = page.images
        # Sort images by vertical position (top to bottom)
        sorted_images = sorted(images, key=lambda im: im['top'])
        print(f"Page {p_idx+1}: {len(sorted_images)} images. Top positions: {[round(im['top'], 1) for im in sorted_images]}")
        # Let's inspect the stream/name of each image
        for i, im in enumerate(sorted_images):
            stream = im.get('stream')
            obj_name = im.get('name')
            print(f"   Photo {i}: name={obj_name}, top={im['top']:.1f}, x0={im['x0']:.1f}")
