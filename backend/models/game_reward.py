"""
Game Reward model - stores rewards earned from games.
"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
import enum


class RewardStatus(str, enum.Enum):
    """Reward status enumeration."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAID = "paid"


class GameReward(Base):
    """Game Reward model for tracking rewards from games."""
    
    __tablename__ = "game_rewards"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Reward Details
    game_type = Column(String(50), nullable=False, index=True)  # block-blast, puzzle, etc.
    score = Column(Integer, nullable=False)
    reward_amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD")
    status = Column(String(20), default=RewardStatus.PENDING.value, nullable=False)
    
    # Additional Info
    game_session_id = Column(String(100), nullable=True)  # Unique game session identifier
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    processed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="game_rewards")
    
    def __repr__(self):
        return f"<GameReward(id={self.id}, game={self.game_type}, score={self.score}, reward={self.reward_amount})>"

