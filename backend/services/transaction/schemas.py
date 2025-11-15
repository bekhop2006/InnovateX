"""
Transaction schemas for request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class TransactionCreate(BaseModel):
    """Schema for creating a transaction."""
    user_id: int = Field(..., description="User ID")
    account_id: int = Field(..., description="Account ID")
    amount: Decimal = Field(..., gt=0, description="Transaction amount (positive)")
    transaction_type: str = Field(..., description="Transaction type: debit, credit, transfer")
    description: Optional[str] = Field(None, description="Transaction description")
    category: Optional[str] = Field(None, description="Transaction category (e.g., food, transport)")


class TransactionRead(BaseModel):
    """Schema for transaction response."""
    id: int
    user_id: int
    account_id: int
    amount: Decimal
    transaction_type: str
    description: Optional[str]
    category: Optional[str]
    status: str
    reference_transaction_id: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


class TransactionFilter(BaseModel):
    """Schema for filtering transactions."""
    user_id: Optional[int] = None
    account_id: Optional[int] = None
    transaction_type: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


class TransactionStats(BaseModel):
    """Schema for transaction statistics."""
    total_transactions: int
    total_debits: Decimal
    total_credits: Decimal
    net_balance: Decimal
    average_transaction: Decimal
    categories: dict

