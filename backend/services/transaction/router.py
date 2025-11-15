"""
Transaction router - API endpoints for transaction management.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import get_db
from .service import (
    create_transaction, get_transaction_by_id, get_transactions_by_user,
    get_transactions_by_account, get_all_transactions, filter_transactions,
    get_transaction_statistics, cancel_transaction
)
from .schemas import (
    TransactionCreate, TransactionRead, TransactionFilter, TransactionStats
)

router = APIRouter()


@router.post("/transactions", response_model=TransactionRead, status_code=201)
async def create_new_transaction(
    transaction_data: TransactionCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new transaction.
    
    - **user_id**: User ID
    - **account_id**: Account ID
    - **amount**: Transaction amount (positive)
    - **transaction_type**: Type (debit, credit, transfer)
    - **description**: Transaction description
    - **category**: Transaction category
    
    Automatically updates account balance.
    Returns created transaction data.
    """
    return create_transaction(transaction_data, db)


@router.get("/transactions", response_model=List[TransactionRead])
async def get_transactions(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    db: Session = Depends(get_db)
):
    """
    Get all transactions with pagination.
    
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum records to return (default: 100, max: 1000)
    
    Returns list of transactions ordered by date (newest first).
    """
    return get_all_transactions(db, skip, limit)


@router.get("/transactions/{transaction_id}", response_model=TransactionRead)
async def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db)
):
    """
    Get transaction by ID.
    
    - **transaction_id**: Transaction ID
    
    Returns transaction data.
    """
    return get_transaction_by_id(transaction_id, db)


@router.get("/transactions/user/{user_id}", response_model=List[TransactionRead])
async def get_user_transactions(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get all transactions for a specific user.
    
    - **user_id**: User ID
    - **skip**: Number of records to skip
    - **limit**: Maximum records to return
    
    Returns list of user's transactions.
    """
    return get_transactions_by_user(user_id, db, skip, limit)


@router.get("/transactions/account/{account_id}", response_model=List[TransactionRead])
async def get_account_transactions(
    account_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get all transactions for a specific account.
    
    - **account_id**: Account ID
    - **skip**: Number of records to skip
    - **limit**: Maximum records to return
    
    Returns list of account's transactions.
    """
    return get_transactions_by_account(account_id, db, skip, limit)


@router.post("/transactions/filter", response_model=List[TransactionRead])
async def filter_transactions_endpoint(
    filters: TransactionFilter,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Filter transactions based on criteria.
    
    - **user_id**: Filter by user ID
    - **account_id**: Filter by account ID
    - **transaction_type**: Filter by type (debit, credit, transfer)
    - **category**: Filter by category
    - **status**: Filter by status
    - **date_from**: Filter by start date
    - **date_to**: Filter by end date
    
    Returns list of filtered transactions.
    """
    return filter_transactions(filters, db, skip, limit)


@router.get("/transactions/stats/summary", response_model=TransactionStats)
async def get_stats(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    account_id: Optional[int] = Query(None, description="Filter by account ID"),
    date_from: Optional[datetime] = Query(None, description="Start date"),
    date_to: Optional[datetime] = Query(None, description="End date"),
    db: Session = Depends(get_db)
):
    """
    Get transaction statistics.
    
    - **user_id**: Filter by user (optional)
    - **account_id**: Filter by account (optional)
    - **date_from**: Start date filter (optional)
    - **date_to**: End date filter (optional)
    
    Returns transaction statistics including totals, averages, and category breakdown.
    """
    return get_transaction_statistics(user_id, account_id, db, date_from, date_to)


@router.post("/transactions/{transaction_id}/cancel", response_model=TransactionRead)
async def cancel_transaction_endpoint(
    transaction_id: int,
    db: Session = Depends(get_db)
):
    """
    Cancel a transaction and reverse balance changes.
    
    - **transaction_id**: Transaction ID
    
    Returns updated transaction data with cancelled status.
    """
    return cancel_transaction(transaction_id, db)


@router.get("/health")
async def transaction_health_check():
    """Health check for transaction service."""
    return {"status": "healthy", "service": "transaction"}

