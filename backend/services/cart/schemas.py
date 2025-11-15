"""
Cart schemas for request/response validation.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from decimal import Decimal


class CartItemCreate(BaseModel):
    """Schema for adding item to cart."""
    user_id: int = Field(..., description="User ID")
    product_id: int = Field(..., description="Product ID")
    quantity: int = Field(default=1, ge=1, description="Quantity (minimum 1)")


class CartItemRead(BaseModel):
    """Schema for cart item response."""
    id: int
    user_id: int
    product_id: int
    quantity: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CartItemWithProduct(BaseModel):
    """Schema for cart item with product details."""
    cart_id: int
    product_id: int
    product_name: str
    product_price: Decimal
    product_image: Optional[str]
    quantity: int
    item_total: Decimal
    in_stock: bool


class CartSummary(BaseModel):
    """Schema for cart summary."""
    user_id: int
    items: List[CartItemWithProduct]
    total_items: int
    total_price: Decimal


class CartItemUpdate(BaseModel):
    """Schema for updating cart item quantity."""
    quantity: int = Field(..., ge=0, description="New quantity (0 to remove)")


class CheckoutRequest(BaseModel):
    """Schema for checkout request."""
    user_id: int = Field(..., description="User ID")
    account_id: int = Field(..., description="Account ID for payment")

