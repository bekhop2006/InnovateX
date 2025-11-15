"""
Transaction model - stores financial transactions.
"""
from sqlalchemy import Column, Integer, String, Numeric, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
import enum


class TransactionType(str, enum.Enum):
    """Transaction type enumeration."""
    DEBIT = "debit"      # Money out
    CREDIT = "credit"    # Money in
    TRANSFER = "transfer"  # Transfer between accounts


class TransactionStatus(str, enum.Enum):
    """Transaction status enumeration."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Transaction(Base):
    """Transaction model for tracking financial operations."""
    
    __tablename__ = "transactions"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Transaction Details
    amount = Column(Numeric(15, 2), nullable=False)
    transaction_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)  # e.g., "food", "transport", "salary"
    status = Column(String(20), default=TransactionStatus.COMPLETED.value, nullable=False)
    
    # Reference for transfers
    reference_transaction_id = Column(Integer, nullable=True)  # For linked transfers
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    account = relationship("Account", back_populates="transactions")
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, type={self.transaction_type}, amount={self.amount}, status={self.status})>"

