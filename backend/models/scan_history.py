"""
ScanHistory model - stores document scan results and metadata.
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, JSON, LargeBinary
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from database import Base


class ScanHistory(Base):
    """Model for storing scan history and results."""
    
    __tablename__ = "scan_history"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Key to User
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Document Information
    document_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)  # Path to stored PDF file or placeholder when stored in DB
    file_mime = Column(String(100), nullable=True, default="application/pdf")
    file_data = Column(LargeBinary, nullable=True)  # Raw PDF bytes when stored in DB
    
    # Scan Metadata
    scan_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)  # scan_date + 90 days
    total_pages = Column(Integer, nullable=False)
    
    # Detection Counters
    qr_count = Column(Integer, default=0)
    signature_count = Column(Integer, default=0)
    stamp_count = Column(Integer, default=0)
    
    # Full Results JSON
    results_json = Column(JSON, nullable=False)  # Complete scan results
    
    # Processing Time
    processing_time = Column(Float, nullable=True)  # Time in seconds
    
    # Relationship
    user = relationship("User", back_populates="scan_history")
    
    def __init__(self, **kwargs):
        """Initialize ScanHistory with automatic expires_at calculation."""
        super().__init__(**kwargs)
        if not self.expires_at and self.scan_date:
            self.expires_at = self.scan_date + timedelta(days=90)
        elif not self.expires_at:
            self.expires_at = datetime.utcnow() + timedelta(days=90)
    
    def __repr__(self):
        return f"<ScanHistory(id={self.id}, user_id={self.user_id}, document={self.document_name})>"

