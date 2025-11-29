"""Bill data extraction service using LLM."""
import json
import logging
import base64
import io
from typing import Dict, List, Optional, Any
from PIL import Image
from openai import OpenAI

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from app.config import config
from app.models import BillItem, PageWiseLineItems, ExtractedData

logger = logging.getLogger(__name__)


class BillExtractionService:
    """Service for extracting structured data from bills using LLM."""
    
    def __init__(self):
        """Initialize extraction service."""
        self.provider = config.LLM_PROVIDER.lower()
        self.openai_client = None
        self.gemini_model = None
        
        if self.provider == "openai" and config.OPENAI_API_KEY:
            self.openai_client = OpenAI(api_key=config.OPENAI_API_KEY)
            logger.info("Using OpenAI for extraction")
        elif self.provider == "gemini" and config.GEMINI_API_KEY and GEMINI_AVAILABLE:
            genai.configure(api_key=config.GEMINI_API_KEY)
            self.gemini_model = genai.GenerativeModel('gemini-2.5-flash')
            logger.info("Using Google Gemini for extraction")
        else:
            logger.warning(f"No LLM provider configured. Provider: {self.provider}")
    
    def image_to_base64(self, image: Image.Image) -> str:
        """
        Convert PIL Image to base64 string.
        
        Args:
            image: PIL Image
            
        Returns:
            Base64 encoded string
        """
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return img_str
    
    def create_extraction_prompt(self) -> str:
        """
        Create prompt for bill extraction.
        
        Returns:
            Extraction prompt
        """
        prompt = """You are an expert at extracting structured data from bills and invoices.

Analyze this bill/invoice image and extract ALL line items with their details. Follow these instructions carefully:

1. **Extract ALL line items**: Don't miss any item. Look for:
   - Item names/descriptions
   - Quantities
   - Rates (price per unit)
   - Amounts (total for that line item)

2. **Page-wise extraction**: If this is a multi-page bill, note which page each item is on.

3. **Identify sub-totals**: If there are sub-totals on any page, include them.

4. **Calculate final total**: Sum all individual line item amounts WITHOUT double-counting:
   - Do NOT include sub-totals in the final sum
   - Do NOT include tax lines if they're already included in item amounts
   - Only sum the actual line item amounts

5. **Extract actual bill total**: Find the final total amount printed on the bill.

6. **Handle edge cases**:
   - Items that span multiple lines
   - Items with discounts
   - Items with taxes
   - Different currencies or units

Return the data in this EXACT JSON format:
```json
{
  "pagewise_line_items": [
    {
      "page_no": "1",
      "bill_items": [
        {
          "item_name": "Item Name",
          "item_amount": 100.00,
          "item_rate": 50.00,
          "item_quantity": 2
        }
      ],
      "sub_total": 100.00
    }
  ],
  "actual_bill_total": 100.00,
  "extraction_notes": "Any important notes about the extraction"
}
```

Important:
- Use null for missing values (rate, quantity, sub_total)
- Ensure all amounts are numbers (not strings)
- Be precise with decimal values
- If you can't determine a value confidently, use null
- Include extraction_notes for any ambiguities or special cases

Return ONLY the JSON, no additional text."""
        
        return prompt
    
    def extract_with_gemini(self, image: Image.Image, ocr_text: str) -> Optional[Dict[str, Any]]:
        """
        Extract bill data using Google Gemini.
        
        Args:
            image: PIL Image of the bill
            ocr_text: OCR extracted text for additional context
            
        Returns:
            Extracted data dictionary
        """
        if not self.gemini_model:
            logger.error("Gemini model not initialized. Please set GEMINI_API_KEY.")
            return None
        
        try:
            # Create prompt
            prompt = self.create_extraction_prompt()
            prompt += f"\n\nOCR Text (for reference):\n{ocr_text[:2000]}"
            
            # Call Gemini with image
            response = self.gemini_model.generate_content([prompt, image])
            content = response.text
            
            # Parse JSON from response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            data = json.loads(content.strip())
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON from Gemini response: {e}")
            logger.error(f"Response content: {content}")
            return None
        except Exception as e:
            logger.error(f"Error in Gemini extraction: {e}")
            return None
    
    def extract_with_vision(self, image: Image.Image, ocr_text: str) -> Optional[Dict[str, Any]]:
        """
        Extract bill data using GPT-4 Vision.
        
        Args:
            image: PIL Image of the bill
            ocr_text: OCR extracted text for additional context
            
        Returns:
            Extracted data dictionary
        """
        if not self.openai_client:
            logger.error("OpenAI client not initialized. Please set OPENAI_API_KEY.")
            return None
        
        try:
            # Convert image to base64
            img_base64 = self.image_to_base64(image)
            
            # Create prompt
            prompt = self.create_extraction_prompt()
            
            # Add OCR text as additional context
            prompt += f"\n\nOCR Text (for reference):\n{ocr_text[:2000]}"
            
            # Call GPT-4 Vision
            response = self.openai_client.chat.completions.create(
                model=config.GPT_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{img_base64}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=config.MAX_TOKENS,
                temperature=config.TEMPERATURE
            )
            
            # Extract response
            content = response.choices[0].message.content
            
            # Parse JSON from response
            # Remove markdown code blocks if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            data = json.loads(content.strip())
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON from LLM response: {e}")
            logger.error(f"Response content: {content}")
            return None
        except Exception as e:
            logger.error(f"Error in vision extraction: {e}")
            return None
    
    def fallback_extraction(self, ocr_text: str) -> Optional[Dict[str, Any]]:
        """
        Fallback extraction using text-only LLM when vision is not available.
        
        Args:
            ocr_text: OCR extracted text
            
        Returns:
            Extracted data dictionary
        """
        if not self.openai_client and not self.gemini_model:
            logger.error("No LLM client initialized. Please set API key.")
            return None
        
        try:
            prompt = self.create_extraction_prompt()
            prompt += f"\n\nBill Text:\n{ocr_text}"
            
            # Try Gemini first if available
            if self.gemini_model:
                response = self.gemini_model.generate_content(prompt)
                content = response.text
            elif self.openai_client:
                response = self.openai_client.chat.completions.create(
                model=config.GPT_FALLBACK_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                    max_tokens=config.MAX_TOKENS,
                    temperature=config.TEMPERATURE
                )
                content = response.choices[0].message.content
            else:
                logger.error("No LLM available for fallback")
                return None
            
            # Parse JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            data = json.loads(content.strip())
            return data
            
        except Exception as e:
            logger.error(f"Error in fallback extraction: {e}")
            return None
    
    def reconcile_amounts(self, extracted_data: Dict[str, Any]) -> ExtractedData:
        """
        Reconcile amounts and calculate final total.
        
        Args:
            extracted_data: Raw extracted data from LLM
            
        Returns:
            Validated and reconciled ExtractedData
        """
        pagewise_items = []
        total_items = 0
        reconciled_amount = 0.0
        
        for page_data in extracted_data.get("pagewise_line_items", []):
            bill_items = []
            
            for item_data in page_data.get("bill_items", []):
                # Create BillItem
                bill_item = BillItem(
                    item_name=item_data.get("item_name", "Unknown"),
                    item_amount=float(item_data.get("item_amount", 0)),
                    item_rate=float(item_data["item_rate"]) if item_data.get("item_rate") is not None else None,
                    item_quantity=float(item_data["item_quantity"]) if item_data.get("item_quantity") is not None else None
                )
                bill_items.append(bill_item)
                
                # Add to reconciled amount (individual items only)
                reconciled_amount += bill_item.item_amount
                total_items += 1
            
            # Create PageWiseLineItems
            page_items = PageWiseLineItems(
                page_no=str(page_data.get("page_no", "1")),
                bill_items=bill_items,
                sub_total=float(page_data["sub_total"]) if page_data.get("sub_total") is not None else None
            )
            pagewise_items.append(page_items)
        
        # Get actual bill total if available
        actual_total = extracted_data.get("actual_bill_total")
        actual_total = float(actual_total) if actual_total is not None else None
        
        # Calculate accuracy
        accuracy = None
        if actual_total and actual_total > 0:
            accuracy = 100 * (1 - abs(reconciled_amount - actual_total) / actual_total)
            accuracy = round(accuracy, 2)
        
        return ExtractedData(
            pagewise_line_items=pagewise_items,
            total_item_count=total_items,
            reconciled_amount=round(reconciled_amount, 2),
            actual_bill_total=round(actual_total, 2) if actual_total else None,
            accuracy_percentage=accuracy
        )
    
    def extract_bill_data(self, image: Image.Image, ocr_text: str) -> Optional[ExtractedData]:
        """
        Extract bill data from image and OCR text.
        
        Args:
            image: PIL Image of the bill
            ocr_text: OCR extracted text
            
        Returns:
            Extracted and reconciled data
        """
        # Try vision extraction based on provider
        if self.provider == "gemini" and self.gemini_model:
            extracted_data = self.extract_with_gemini(image, ocr_text)
        elif self.provider == "openai" and self.openai_client:
            extracted_data = self.extract_with_vision(image, ocr_text)
        else:
            extracted_data = None
        
        # Fallback to text-only if vision fails
        if not extracted_data:
            logger.warning("Vision extraction failed, trying text-only fallback")
            extracted_data = self.fallback_extraction(ocr_text)
        
        if not extracted_data:
            logger.error("Both vision and fallback extraction failed")
            return None
        
        # Reconcile and validate
        try:
            reconciled_data = self.reconcile_amounts(extracted_data)
            return reconciled_data
        except Exception as e:
            logger.error(f"Error reconciling data: {e}")
            return None


# Singleton instance
extraction_service = BillExtractionService()

