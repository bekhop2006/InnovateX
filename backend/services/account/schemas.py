"""
Account schemas for request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class AccountCreate(BaseModel):
    """Schema for creating a new account."""
    user_id: int = Field(..., description="User ID who owns the account")
    account_type: str = Field(..., description="Account type: checking, savings, credit")
    currency: str = Field(default="USD", description="Account currency (USD, EUR, KZT, etc.)")
    initial_balance: Optional[Decimal] = Field(default=Decimal("0.00"), description="Initial balance")


class AccountRead(BaseModel):
    """Schema for account response."""
    id: int
    user_id: int
    account_type: str
    balance: Decimal
    currency: str
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AccountUpdate(BaseModel):
    """Schema for updating account."""
    status: Optional[str] = Field(None, description="Account status: active, blocked, closed")
    currency: Optional[str] = Field(None, description="Account currency")


class BalanceUpdate(BaseModel):
    """Schema for updating account balance."""
    amount: Decimal = Field(..., description="Amount to add (positive) or subtract (negative)")
    description: Optional[str] = Field(None, description="Description of the balance change")


class TransferRequest(BaseModel):
    """Schema for transferring money between accounts."""
    from_account_id: int = Field(..., description="Source account ID")
    to_account_id: int = Field(..., description="Destination account ID")
    amount: Decimal = Field(..., gt=0, description="Amount to transfer (must be positive)")
    description: Optional[str] = Field(None, description="Transfer description")

