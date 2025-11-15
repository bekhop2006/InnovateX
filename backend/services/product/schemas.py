"""
Product schemas for request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class ProductCreate(BaseModel):
    """Schema for creating a product."""
    name: str = Field(..., min_length=1, max_length=255, description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    price: Decimal = Field(..., gt=0, description="Product price (must be positive)")
    category: Optional[str] = Field(None, max_length=100, description="Product category")
    stock: int = Field(default=0, ge=0, description="Stock quantity")
    image_url: Optional[str] = Field(None, max_length=500, description="Product image URL")
    sku: Optional[str] = Field(None, max_length=100, description="Stock Keeping Unit")


class ProductRead(BaseModel):
    """Schema for product response."""
    id: int
    name: str
    description: Optional[str]
    price: Decimal
    category: Optional[str]
    stock: int
    image_url: Optional[str]
    sku: Optional[str]
    is_active: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProductUpdate(BaseModel):
    """Schema for updating a product."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0)
    category: Optional[str] = Field(None, max_length=100)
    stock: Optional[int] = Field(None, ge=0)
    image_url: Optional[str] = Field(None, max_length=500)
    sku: Optional[str] = Field(None, max_length=100)
    is_active: Optional[int] = Field(None, ge=0, le=1)


class ProductSearch(BaseModel):
    """Schema for product search."""
    query: Optional[str] = None
    category: Optional[str] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    in_stock_only: bool = False

