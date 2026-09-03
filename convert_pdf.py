import os
import pdfplumber

def convert_pdf_to_png(pdf_name, output_png_name):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(base_dir, pdf_name)
    output_dir = os.path.join(base_dir, "assets")
    output_path = os.path.join(output_dir, output_png_name)
    
    if not os.path.exists(pdf_path):
        print(f"Error: {pdf_name} does not exist.")
        return False
        
    print(f"Opening {pdf_name}...")
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if not pdf.pages:
                print("Error: No pages found in PDF.")
                return False
            page = pdf.pages[0]
            print("Rendering page to image...")
            # to_image renders the page. resolution=150 is standard.
            im = page.to_image(resolution=150)
            print(f"Saving to {output_png_name}...")
            im.save(output_path, format="PNG")
            print("Success!")
            return True
    except Exception as e:
        print(f"Failed to convert {pdf_name}: {e}")
        return False

if __name__ == "__main__":
    convert_pdf_to_png("test_output_classic_ats.pdf", "classic_ats.png")
    convert_pdf_to_png("test_output_elegant_executive.pdf", "elegant_executive.png")
    convert_pdf_to_png("test_output_modern_minimalist.pdf", "modern_minimalist.png")
