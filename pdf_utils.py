import fitz  # PyMuPDF
from typing import List
import re
import io
import os

# Try to import OCR libraries, fallback gracefully if not available
try:
    import pytesseract
    from PIL import Image
    import cv2
    import numpy as np
    OCR_AVAILABLE = True
    
    # Set tesseract path for Windows (common installation paths)
    import platform
    if platform.system() == "Windows":
        possible_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            r"C:\Users\{}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe".format(os.getenv('USERNAME', '')),
            r"C:\tools\tesseract\tesseract.exe",
            "tesseract.exe"  # Try system PATH
        ]
        
        tesseract_found = False
        for path in possible_paths:
            try:
                if path == "tesseract.exe":
                    # Test if it's in PATH
                    pytesseract.pytesseract.tesseract_cmd = path
                    pytesseract.get_tesseract_version()
                    tesseract_found = True
                    break
                elif os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    pytesseract.get_tesseract_version()
                    tesseract_found = True
                    print(f"Found Tesseract at: {path}")
                    break
            except:
                continue
        
        if not tesseract_found:
            print("Tesseract installed but not found in common paths")
except ImportError:
    OCR_AVAILABLE = False
    print("OCR libraries not available. Install pytesseract, Pillow, and opencv-python for image support.")

def check_ocr_setup():
    """Check if OCR is properly set up"""
    if not OCR_AVAILABLE:
        return False, "OCR libraries not installed"
    
    try:
        # Test if tesseract is working
        version = pytesseract.get_tesseract_version()
        return True, f"OCR ready (Tesseract v{version})"
    except Exception as e:
        return False, f"Tesseract OCR engine not found: {str(e)}"

def get_ocr_install_instructions():
    """Get installation instructions for OCR"""
    return """
    ## 📷 To Enable Image OCR Support:
    
    ### Windows (Recommended):
    ```bash
    winget install --id UB-Mannheim.TesseractOCR
    ```
    
    ### Alternative Windows Methods:
    1. **Direct Download**: https://github.com/UB-Mannheim/tesseract/wiki
    2. **Chocolatey**: `choco install tesseract`
    3. **Scoop**: `scoop install tesseract`
    
    ### After Installation:
    - Restart your terminal/command prompt
    - Restart the Streamlit application
    - OCR should be automatically detected
    
    ### Troubleshooting:
    - Make sure Tesseract is in your system PATH
    - Try restarting your computer if still not detected
    - Check installation in: `C:\\Program Files\\Tesseract-OCR\\`
    """

def preprocess_image_for_ocr(image):
    """Preprocess image for better OCR results"""
    if not OCR_AVAILABLE:
        return None
        
    try:
        # Convert PIL image to OpenCV format
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Convert to grayscale
        gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
        
        # Apply denoising
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        
        return thresh
    except Exception as e:
        print(f"Image preprocessing error: {e}")
        return None

def extract_text_from_image(image_path_or_bytes):
    """Extract text from image using OCR"""
    if not OCR_AVAILABLE:
        return "OCR not available. Please install Tesseract OCR."
    
    try:
        if isinstance(image_path_or_bytes, bytes):
            # If bytes, convert to PIL Image
            image = Image.open(io.BytesIO(image_path_or_bytes))
        else:
            # If file path, open directly
            image = Image.open(image_path_or_bytes)
        
        # Try simple OCR first
        try:
            text = pytesseract.image_to_string(image, config='--psm 6')
            if text.strip():
                return text.strip()
        except Exception as e:
            print(f"Simple OCR failed: {e}")
        
        # If simple OCR fails, try with preprocessing
        processed_image = preprocess_image_for_ocr(image)
        if processed_image is not None:
            text = pytesseract.image_to_string(processed_image, config='--psm 6')
            return text.strip()
        
        return ""
    except Exception as e:
        print(f"OCR Error: {e}")
        return f"OCR Error: {str(e)}"

def extract_text_from_pdf(pdf_path: str, use_ocr: bool = True) -> str:
    """Extract text from PDF, including OCR for images when available"""
    doc = fitz.open(pdf_path)
    text = ""
    ocr_pages_used = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # First, try to extract text normally
        page_text = page.get_text()
        
        # If no text found or very little text, try OCR on the page image
        if use_ocr and OCR_AVAILABLE and (not page_text.strip() or len(page_text.strip()) < 50):
            try:
                # Render page as image
                mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better OCR
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.tobytes("png")
                
                # Extract text using OCR
                ocr_text = extract_text_from_image(img_data)
                
                if ocr_text.strip() and not ocr_text.startswith("OCR Error"):
                    page_text = ocr_text
                    ocr_pages_used.append(page_num + 1)
                    print(f"Used OCR for page {page_num + 1}")
                
            except Exception as e:
                print(f"OCR failed for page {page_num + 1}: {e}")
        
        text += page_text + "\n"
    
    doc.close()
    
    if ocr_pages_used:
        print(f"OCR was used for pages: {ocr_pages_used}")
    
    return text

def extract_text_from_image_file(image_path: str) -> str:
    """Extract text from standalone image file"""
    if not OCR_AVAILABLE:
        return "OCR not available. Please install Tesseract OCR to extract text from images."
    
    return extract_text_from_image(image_path)

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Split text into chunks with overlap"""
    # Split text into words
    words = re.findall(r'\w+|[\.,!?;\-\n]', text)
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = ' '.join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks 