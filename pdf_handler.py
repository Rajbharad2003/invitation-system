"""
PDF Handler Module
Handles PDF manipulation - adding names to specific positions in PDFs
"""
import fitz  # PyMuPDF
import os
from typing import Tuple, Optional


def add_name_to_pdf(
    pdf_path: str,
    name: str,
    x: float,
    y: float,
    page_num: int = 0,
    font_size: int = 24,
    font_color: Tuple[float, float, float] = (0, 0, 0),
    font_name: str = "helv",
    font_path: Optional[str] = None,
    output_path: Optional[str] = None
) -> str:
    """
    Add a name to a PDF at the specified position.
    
    Args:
        pdf_path: Path to the source PDF file
        name: The name to add to the PDF
        x: X coordinate (from left)
        y: Y coordinate (from top)
        page_num: Page number (0-indexed)
        font_size: Font size for the name
        font_color: RGB tuple (0-1 range) for font color
        font_name: Font name (helv, times-roman, courier, etc.)
        output_path: Where to save the modified PDF (if None, generates one)
    
    Returns:
        Path to the generated PDF file
    """
    # Open the PDF
    doc = fitz.open(pdf_path)
    
    # Get the specified page
    if page_num >= len(doc):
        page_num = 0
    page = doc[page_num]
    
    
    # Register font if path provided and file exists
    font_key = font_name
    if font_path and os.path.exists(font_path):
        try:
            font_key = "custom_font"
            page.insert_font(fontfile=font_path, fontname=font_key)
        except Exception as e:
            print(f"Error loading font: {e}")
            font_key = font_name # Fallback

    # Create insertion point
    point = fitz.Point(x, y)
    
    # Insert the text
    # render_mode=0 is for normal fill text
    try:
        page.insert_text(
            point,
            name,
            fontname=font_key,
            fontsize=font_size,
            color=font_color,
            render_mode=0
        )
    except Exception as e:
         print(f"Error inserting text: {e}")
         # Fallback to helv if custom font fails entirely
         page.insert_text(
            point,
            name,
            fontname="helv",
            fontsize=font_size,
            color=font_color
        )
    
    # Generate output path if not provided
    if output_path is None:
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        # logic for filename moved to caller or kept simple here
        # taking first 15 chars of name for filename as requested
        safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip() 
        safe_name = safe_name.replace(' ', '_')[:15]
        
        output_dir = os.path.join(os.path.dirname(pdf_path), '..', 'output')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{base_name}_{safe_name}.pdf")
    
    # Save the modified PDF
    doc.save(output_path)
    doc.close()
    
    return output_path


def get_pdf_preview(pdf_path: str, page_num: int = 0, zoom: float = 1.5) -> bytes:
    """
    Generate a PNG preview of a PDF page.
    
    Args:
        pdf_path: Path to the PDF file
        page_num: Page number to preview (0-indexed)
        zoom: Zoom factor for the preview
    
    Returns:
        PNG image as bytes
    """
    doc = fitz.open(pdf_path)
    
    if page_num >= len(doc):
        page_num = 0
    
    page = doc[page_num]
    
    # Create a matrix for zooming
    mat = fitz.Matrix(zoom, zoom)
    
    # Render page to a pixmap
    pix = page.get_pixmap(matrix=mat)
    
    # Get PNG bytes
    png_bytes = pix.tobytes("png")
    
    doc.close()
    
    return png_bytes


def get_pdf_dimensions(pdf_path: str, page_num: int = 0) -> Tuple[float, float]:
    """
    Get the dimensions of a PDF page.
    
    Args:
        pdf_path: Path to the PDF file
        page_num: Page number (0-indexed)
    
    Returns:
        Tuple of (width, height) in points
    """
    doc = fitz.open(pdf_path)
    
    if page_num >= len(doc):
        page_num = 0
    
    page = doc[page_num]
    rect = page.rect
    
    doc.close()
    
    return (rect.width, rect.height)


def get_pdf_page_count(pdf_path: str) -> int:
    """
    Get the number of pages in a PDF.
    
    Args:
        pdf_path: Path to the PDF file
    
    Returns:
        Number of pages
    """
    doc = fitz.open(pdf_path)
    count = len(doc)
    doc.close()
    return count
