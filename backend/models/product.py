"""
Product model - stores e-commerce products.
"""
from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Product(Base):
    """Product model for e-commerce functionality."""
    
    __tablename__ = "products"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Product Details
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    category = Column(String(100), nullable=True, index=True)
    stock = Column(Integer, default=0, nullable=False)
    image_url = Column(String(500), nullable=True)
    
    # Additional Details
    sku = Column(String(100), unique=True, nullable=True)  # Stock Keeping Unit
    is_active = Column(Integer, default=1)  # 1 = active, 0 = inactive
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    cart_items = relationship("Cart", back_populates="product", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Product(id={self.id}, name={self.name}, price={self.price}, stock={self.stock})>"

