"""
Financial Goal model - stores user financial goals.
"""
from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
import enum


class GoalStatus(str, enum.Enum):
    """Goal status enumeration."""
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class FinancialGoal(Base):
    """Financial Goal model for tracking savings goals."""
    
    __tablename__ = "financial_goals"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Goal Details
    title = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    target_amount = Column(Numeric(15, 2), nullable=False)
    current_amount = Column(Numeric(15, 2), default=0.00, nullable=False)
    deadline = Column(Date, nullable=True)
    status = Column(String(20), default=GoalStatus.ACTIVE.value, nullable=False)
    
    # Progress tracking
    currency = Column(String(3), default="USD")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="financial_goals")
    
    @property
    def progress_percentage(self):
        """Calculate progress percentage."""
        if self.target_amount == 0:
            return 0
        return min(100, (float(self.current_amount) / float(self.target_amount)) * 100)
    
    def __repr__(self):
        return f"<FinancialGoal(id={self.id}, title={self.title}, progress={self.progress_percentage:.1f}%)>"

