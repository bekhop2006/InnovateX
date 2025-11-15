"""
Crypto Trade model - stores cryptocurrency trade history.
"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
import enum


class TradeType(str, enum.Enum):
    """Trade type enumeration."""
    BUY = "buy"
    SELL = "sell"


class TradeStatus(str, enum.Enum):
    """Trade status enumeration."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CryptoTrade(Base):
    """Crypto Trade model for tracking buy/sell operations."""
    
    __tablename__ = "crypto_trades"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Trade Details
    symbol = Column(String(10), nullable=False, index=True)  # BTC, ETH, etc.
    trade_type = Column(String(10), nullable=False)  # buy or sell
    amount = Column(Numeric(20, 8), nullable=False)  # Amount of crypto
    price_usd = Column(Numeric(15, 2), nullable=False)  # Price per unit in USD
    total_usd = Column(Numeric(15, 2), nullable=False)  # Total transaction value
    fee_usd = Column(Numeric(10, 2), default=0.00)  # Transaction fee
    status = Column(String(20), default=TradeStatus.COMPLETED.value, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="crypto_trades")
    
    def __repr__(self):
        return f"<CryptoTrade(id={self.id}, type={self.trade_type}, symbol={self.symbol}, amount={self.amount})>"

