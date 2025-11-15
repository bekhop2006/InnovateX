"""
Crypto Price Cache model - caches cryptocurrency prices.
"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime
from datetime import datetime
from database import Base


class CryptoPriceCache(Base):
    """Crypto Price Cache model for caching real-time prices."""
    
    __tablename__ = "crypto_price_cache"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Price Details
    symbol = Column(String(10), unique=True, nullable=False, index=True)  # BTC, ETH, etc.
    price_usd = Column(Numeric(15, 2), nullable=False)
    price_change_24h = Column(Numeric(10, 2), nullable=True)  # Percentage change
    market_cap = Column(Numeric(20, 2), nullable=True)
    volume_24h = Column(Numeric(20, 2), nullable=True)
    
    # Timestamps
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<CryptoPriceCache(symbol={self.symbol}, price={self.price_usd} USD)>"

