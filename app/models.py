"""Pydantic models for request/response validation."""
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl


class BillItem(BaseModel):
    """Individual line item in a bill."""
    item_name: str = Field(..., description="Name of the item")
    item_amount: float = Field(..., description="Total amount for this line item")
    item_rate: Optional[float] = Field(None, description="Rate per unit")
    item_quantity: Optional[float] = Field(None, description="Quantity of items")


class PageWiseLineItems(BaseModel):
    """Line items grouped by page."""
    page_no: str = Field(..., description="Page number")
    bill_items: List[BillItem] = Field(..., description="List of items on this page")
    sub_total: Optional[float] = Field(None, description="Subtotal for this page if exists")


class ExtractedData(BaseModel):
    """Extracted bill data."""
    pagewise_line_items: List[PageWiseLineItems] = Field(..., description="Line items grouped by page")
    total_item_count: int = Field(..., description="Total number of line items")
    reconciled_amount: float = Field(..., description="Final total amount without double counting")
    actual_bill_total: Optional[float] = Field(None, description="Total amount as per bill")
    accuracy_percentage: Optional[float] = Field(None, description="Accuracy of extraction")


class BillExtractionRequest(BaseModel):
    """Request model for bill extraction."""
    document: str = Field(..., description="URL or path to the document")


class BillExtractionResponse(BaseModel):
    """Response model for bill extraction."""
    is_success: bool = Field(..., description="Whether extraction was successful")
    data: Optional[ExtractedData] = Field(None, description="Extracted data")
    error: Optional[str] = Field(None, description="Error message if any")

