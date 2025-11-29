"""OCR service for extracting text from images."""
import io
import logging
from typing import Optional, List
from PIL import Image
import requests
import pytesseract
import easyocr
import numpy as np
import cv2

try:
    from pdf2image import convert_from_bytes
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    logger.warning("pdf2image not available. PDF support disabled.")

from app.config import config

logger = logging.getLogger(__name__)


class OCRService:
    """Service for performing OCR on images."""
    
    def __init__(self):
        """Initialize OCR service."""
        self.engine = config.OCR_ENGINE
        self.easyocr_reader = None
        
        if self.engine == "easyocr":
            logger.info("Initializing EasyOCR reader...")
            self.easyocr_reader = easyocr.Reader(['en'], gpu=False)
    
    def download_image(self, url: str) -> Optional[Image.Image]:
        """
        Download image from URL. Supports both images and PDFs.
        
        Args:
            url: URL of the image or PDF
            
        Returns:
            PIL Image object or None if failed
        """
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            content = response.content
            
            # Try to open as image first
            try:
                image = Image.open(io.BytesIO(content))
                return image
            except Exception as img_error:
                # If image opening fails, try PDF conversion
                if PDF_SUPPORT and (url.lower().endswith('.pdf') or 'pdf' in url.lower()):
                    logger.info("Detected PDF file, converting to image...")
                    try:
                        # Convert first page of PDF to image
                        images = convert_from_bytes(content, first_page=1, last_page=1, dpi=300)
                        if images:
                            logger.info("Successfully converted PDF to image")
                            return images[0]
                    except Exception as pdf_error:
                        logger.error(f"Error converting PDF: {pdf_error}")
                        raise pdf_error
                else:
                    raise img_error
                    
        except Exception as e:
            logger.error(f"Error downloading/processing document from {url}: {e}")
            return None
    
    def preprocess_image(self, image: Image.Image) -> np.ndarray:
        """
        Preprocess image for better OCR results.
        
        Args:
            image: PIL Image
            
        Returns:
            Preprocessed numpy array
        """
        # Convert to numpy array
        img_array = np.array(image)
        
        # Convert to grayscale if needed
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # Apply adaptive thresholding for better contrast
        processed = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # Denoise
        processed = cv2.fastNlMeansDenoising(processed, None, 10, 7, 21)
        
        return processed
    
    def extract_text_easyocr(self, image: Image.Image) -> str:
        """
        Extract text using EasyOCR.
        
        Args:
            image: PIL Image
            
        Returns:
            Extracted text
        """
        try:
            # Convert image to numpy array
            img_array = np.array(image)
            
            # Perform OCR
            results = self.easyocr_reader.readtext(img_array, detail=0, paragraph=True)
            
            # Join results
            text = "\n".join(results)
            return text
        except Exception as e:
            logger.error(f"Error in EasyOCR extraction: {e}")
            return ""
    
    def extract_text_tesseract(self, image: Image.Image) -> str:
        """
        Extract text using Tesseract.
        
        Args:
            image: PIL Image
            
        Returns:
            Extracted text
        """
        try:
            # Preprocess image
            processed = self.preprocess_image(image)
            
            # Perform OCR
            text = pytesseract.image_to_string(processed)
            return text
        except Exception as e:
            logger.error(f"Error in Tesseract extraction: {e}")
            return ""
    
    def extract_text(self, image: Image.Image) -> str:
        """
        Extract text from image using configured OCR engine.
        
        Args:
            image: PIL Image
            
        Returns:
            Extracted text
        """
        if self.engine == "easyocr":
            return self.extract_text_easyocr(image)
        elif self.engine == "tesseract":
            return self.extract_text_tesseract(image)
        else:
            logger.warning(f"Unknown OCR engine: {self.engine}, defaulting to EasyOCR")
            return self.extract_text_easyocr(image)
    
    def process_document(self, document_url: str) -> Optional[dict]:
        """
        Process document and extract text.
        
        Args:
            document_url: URL of the document
            
        Returns:
            Dictionary with extracted text and metadata
        """
        try:
            # Download image
            image = self.download_image(document_url)
            if image is None:
                return None
            
            # Extract text
            text = self.extract_text(image)
            
            return {
                "text": text,
                "image": image,
                "width": image.width,
                "height": image.height
            }
        except Exception as e:
            logger.error(f"Error processing document: {e}")
            return None


# Singleton instance
ocr_service = OCRService()

