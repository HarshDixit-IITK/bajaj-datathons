"""Main FastAPI application."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import config
from app.models import BillExtractionRequest, BillExtractionResponse, ExtractedData
from app.ocr_service import ocr_service
from app.extraction_service import extraction_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("Starting Bill Data Extraction API...")
    logger.info(f"OCR Engine: {config.OCR_ENGINE}")
    logger.info(f"GPT Model: {config.GPT_MODEL}")
    yield
    logger.info("Shutting down Bill Data Extraction API...")


# Create FastAPI app
app = FastAPI(
    title="Bill Data Extraction API",
    description="Extract line items and amounts from bill/invoice images",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Bill Data Extraction API",
        "version": "1.0.0",
        "endpoints": {
            "extract": "/extract-bill-data",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "ocr_engine": config.OCR_ENGINE,
        "gpt_model": config.GPT_MODEL,
        "openai_configured": bool(config.OPENAI_API_KEY)
    }


@app.post("/extract-bill-data", response_model=BillExtractionResponse)
async def extract_bill_data(request: BillExtractionRequest):
    """
    Extract line items and amounts from a bill/invoice.
    
    Args:
        request: Bill extraction request with document URL
        
    Returns:
        Extracted bill data with line items and amounts
    """
    try:
        logger.info(f"Processing document: {request.document}")
        
        # Step 1: Perform OCR
        logger.info("Step 1: Performing OCR...")
        ocr_result = ocr_service.process_document(request.document)
        
        if not ocr_result:
            raise HTTPException(
                status_code=400,
                detail="Failed to process document. Please check the document URL."
            )
        
        logger.info(f"OCR completed. Extracted {len(ocr_result['text'])} characters")
        
        # Step 2: Extract structured data using LLM
        logger.info("Step 2: Extracting structured data with LLM...")
        extracted_data = extraction_service.extract_bill_data(
            ocr_result['image'],
            ocr_result['text']
        )
        
        if not extracted_data:
            raise HTTPException(
                status_code=500,
                detail="Failed to extract bill data. Please check your OpenAI API key."
            )
        
        logger.info(f"Extraction completed. Found {extracted_data.total_item_count} items")
        logger.info(f"Reconciled amount: {extracted_data.reconciled_amount}")
        if extracted_data.accuracy_percentage:
            logger.info(f"Accuracy: {extracted_data.accuracy_percentage}%")
        
        # Step 3: Return response
        return BillExtractionResponse(
            is_success=True,
            data=extracted_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)
        return BillExtractionResponse(
            is_success=False,
            error=str(e)
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=True
    )

