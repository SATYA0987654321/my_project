import shutil
import os

def copy_files_to_desktop():
    desktop_dir = r"C:\Users\krbha\OneDrive\Desktop"
    
    pdf_source = "proposal.pdf"
    html_source = "proposal.html"
    
    pdf_dest = os.path.join(desktop_dir, "proposal.pdf")
    html_dest = os.path.join(desktop_dir, "proposal.html")
    
    copied = []
    
    if os.path.exists(pdf_source):
        shutil.copy2(pdf_source, pdf_dest)
        copied.append("proposal.pdf")
        
    if os.path.exists(html_source):
        shutil.copy2(html_source, html_dest)
        copied.append("proposal.html")
        
    if copied:
        print(f"Success: Copied {', '.join(copied)} to your Desktop.")
    else:
        print("Error: Files not found to copy.")

if __name__ == '__main__':
    copy_files_to_desktop()
