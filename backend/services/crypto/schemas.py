"""
Crypto schemas for request/response validation.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from decimal import Decimal


class CryptoAssetRead(BaseModel):
    """Schema for crypto asset response."""
    id: int
    account_id: int
    symbol: str
    name: Optional[str]
    amount: Decimal
    average_buy_price: Optional[Decimal]
    current_price: Optional[Decimal] = None
    current_value: Optional[Decimal] = None
    profit_loss: Optional[Decimal] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CryptoPortfolio(BaseModel):
    """Schema for crypto portfolio."""
    user_id: int
    account_id: int
    assets: List[CryptoAssetRead]
    total_value_usd: Decimal
    total_investment: Decimal
    total_profit_loss: Decimal


class TradeRequest(BaseModel):
    """Schema for trade request."""
    user_id: int = Field(..., description="User ID")
    symbol: str = Field(..., description="Crypto symbol (e.g., BTC, ETH)")
    trade_type: str = Field(..., description="Trade type: buy or sell")
    amount: Decimal = Field(..., gt=0, description="Amount of crypto")
    account_id: int = Field(..., description="Account ID for funding")


class TradeRead(BaseModel):
    """Schema for trade response."""
    id: int
    user_id: int
    symbol: str
    trade_type: str
    amount: Decimal
    price_usd: Decimal
    total_usd: Decimal
    fee_usd: Decimal
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class PriceRead(BaseModel):
    """Schema for crypto price."""
    symbol: str
    price_usd: Decimal
    price_change_24h: Optional[Decimal]
    market_cap: Optional[Decimal]
    volume_24h: Optional[Decimal]
    last_updated: datetime
    
    class Config:
        from_attributes = True

