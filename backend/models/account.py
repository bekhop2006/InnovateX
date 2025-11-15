"""
Account model - stores user financial accounts.
"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
import enum


class AccountType(str, enum.Enum):
    """Account type enumeration."""
    CHECKING = "checking"
    SAVINGS = "savings"
    CREDIT = "credit"


class AccountStatus(str, enum.Enum):
    """Account status enumeration."""
    ACTIVE = "active"
    BLOCKED = "blocked"
    CLOSED = "closed"


class Account(Base):
    """Account model for managing user financial accounts."""
    
    __tablename__ = "accounts"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Account Details
    account_type = Column(String(50), nullable=False, default=AccountType.CHECKING.value)
    balance = Column(Numeric(15, 2), default=0.00, nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    status = Column(String(20), default=AccountStatus.ACTIVE.value, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)  # Soft delete
    
    # Relationships
    user = relationship("User", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Account(id={self.id}, user_id={self.user_id}, type={self.account_type}, balance={self.balance})>"

