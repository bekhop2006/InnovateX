"""
Cleanup service for deleting expired scans.
"""
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from database import SessionLocal
from .service import delete_expired_scans
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def cleanup_expired_scans():
    """
    Cleanup function that runs periodically to delete expired scans.
    Runs every day at 3 AM.
    """
    logger.info("Starting cleanup of expired scans...")
    
    db: Session = SessionLocal()
    try:
        result = delete_expired_scans(db)
        logger.info(f"Cleanup complete. Deleted {result['deleted_count']} expired scans.")
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")
    finally:
        db.close()


# Create scheduler
scheduler = BackgroundScheduler()


def start_cleanup_scheduler():
    """Start the cleanup scheduler."""
    # Run cleanup every day at 3 AM
    scheduler.add_job(
        cleanup_expired_scans,
        'cron',
        hour=3,
        minute=0,
        id='cleanup_expired_scans',
        name='Cleanup expired scans',
        replace_existing=True
    )
    
    if not scheduler.running:
        scheduler.start()
        logger.info("Cleanup scheduler started. Will run daily at 3:00 AM.")


def stop_cleanup_scheduler():
    """Stop the cleanup scheduler."""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Cleanup scheduler stopped.")

