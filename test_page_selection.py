
import fitz
import os
from pdf_handler import add_name_to_pdf

def test_add_name_on_page_2():
    # Create a dummy 3-page PDF
    doc = fitz.open()
    for i in range(3):
        page = doc.new_page()
        page.insert_text((50, 50), f"Page {i+1}")
    
    test_pdf_path = "test_multipage.pdf"
    doc.save(test_pdf_path)
    doc.close()
    
    print(f"Created {test_pdf_path}")
    
    # Add name to page 1 (index 1)
    output_path = "test_output.pdf"
    add_name_to_pdf(
        pdf_path=test_pdf_path,
        name="TestUser",
        x=100,
        y=100,
        page_num=1, # Page 2
        output_path=output_path
    )
    
    # Verify
    doc = fitz.open(output_path)
    page2 = doc[1]
    text = page2.get_text()
    if "TestUser" in text:
        print("SUCCESS: Name found on Page 2")
    else:
        print("FAILURE: Name NOT found on Page 2")
        
    page1 = doc[0]
    if "TestUser" in page1.get_text():
        print("FAILURE: Name found on Page 1 (should not be there)")
    else:
        print("SUCCESS: Name NOT found on Page 1")

    # Clean up
    os.remove(test_pdf_path)
    os.remove(output_path)

if __name__ == "__main__":
    test_add_name_on_page_2()
