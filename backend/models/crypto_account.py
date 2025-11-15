"""
Crypto Account model - stores user crypto portfolio account.
"""
from sqlalchemy import Column, Integer, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class CryptoAccount(Base):
    """Crypto Account model for managing cryptocurrency portfolios."""
    
    __tablename__ = "crypto_accounts"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys (one-to-one with User)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    
    # Account Details
    total_value_usd = Column(Numeric(15, 2), default=0.00, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="crypto_account")
    assets = relationship("CryptoAsset", back_populates="account", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<CryptoAccount(id={self.id}, user_id={self.user_id}, total_value={self.total_value_usd} USD)>"

