"""
Crypto Asset model - stores individual cryptocurrency holdings.
"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class CryptoAsset(Base):
    """Crypto Asset model for individual cryptocurrency holdings."""
    
    __tablename__ = "crypto_assets"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    account_id = Column(Integer, ForeignKey("crypto_accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Asset Details
    symbol = Column(String(10), nullable=False, index=True)  # BTC, ETH, etc.
    name = Column(String(100), nullable=True)  # Bitcoin, Ethereum, etc.
    amount = Column(Numeric(20, 8), nullable=False)  # Amount held
    average_buy_price = Column(Numeric(15, 2), nullable=True)  # Average purchase price in USD
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    account = relationship("CryptoAccount", back_populates="assets")
    
    def __repr__(self):
        return f"<CryptoAsset(id={self.id}, symbol={self.symbol}, amount={self.amount})>"

