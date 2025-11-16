"""
Database configuration and session management.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy import inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./innovatex.db")

# Create SQLAlchemy engine
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=os.getenv("DEBUG", "False").lower() == "true"
    )
else:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        echo=os.getenv("DEBUG", "False").lower() == "true"
    )

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


def get_db():
    """
    Dependency for getting database session.
    Automatically closes the session after request completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all tables in the database."""
    Base.metadata.create_all(bind=engine)


def ensure_scan_history_blob_columns():
    """Ensure scan_history has file_data and file_mime columns for DB storage of PDFs."""
    try:
        inspector = inspect(engine)
        cols = {c['name'] for c in inspector.get_columns('scan_history')}
        dialect = engine.dialect.name
        with engine.begin() as conn:
            if 'file_mime' not in cols:
                if dialect == 'postgresql':
                    conn.execute(text('ALTER TABLE scan_history ADD COLUMN file_mime VARCHAR(100)'))
                else:
                    conn.execute(text('ALTER TABLE scan_history ADD COLUMN file_mime VARCHAR(100)'))
            if 'file_data' not in cols:
                if dialect == 'postgresql':
                    conn.execute(text('ALTER TABLE scan_history ADD COLUMN file_data BYTEA'))
                else:
                    conn.execute(text('ALTER TABLE scan_history ADD COLUMN file_data BLOB'))
    except Exception:
        pass


def drop_tables():
    """Drop all tables in the database (use with caution!)"""
    Base.metadata.drop_all(bind=engine)

