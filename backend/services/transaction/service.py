"""
Transaction service - business logic for transaction management.
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from fastapi import HTTPException, status
from typing import List, Optional
from decimal import Decimal
from datetime import datetime

from models.transaction import Transaction, TransactionType, TransactionStatus
from models.account import Account
from models.user import User
from .schemas import TransactionCreate, TransactionRead, TransactionFilter, TransactionStats


def create_transaction(transaction_data: TransactionCreate, db: Session) -> TransactionRead:
    """
    Create a new transaction.
    
    Args:
        transaction_data: Transaction creation data
        db: Database session
        
    Returns:
        Created transaction data
        
    Raises:
        HTTPException: If user/account doesn't exist or invalid data
    """
    # Verify user exists
    user = db.query(User).filter(User.id == transaction_data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify account exists and belongs to user
    account = db.query(Account).filter(
        Account.id == transaction_data.account_id,
        Account.user_id == transaction_data.user_id
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found or doesn't belong to user"
        )
    
    # Validate transaction type
    valid_types = [t.value for t in TransactionType]
    if transaction_data.transaction_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid transaction type. Must be one of: {', '.join(valid_types)}"
        )
    
    # Check sufficient funds for debit transactions
    if transaction_data.transaction_type == TransactionType.DEBIT.value:
        if account.balance < transaction_data.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient funds"
            )
    
    try:
        # Create transaction
        new_transaction = Transaction(
            user_id=transaction_data.user_id,
            account_id=transaction_data.account_id,
            amount=transaction_data.amount,
            transaction_type=transaction_data.transaction_type,
            description=transaction_data.description,
            category=transaction_data.category,
            status=TransactionStatus.COMPLETED.value
        )
        
        # Update account balance
        if transaction_data.transaction_type == TransactionType.DEBIT.value:
            account.balance -= transaction_data.amount
        elif transaction_data.transaction_type == TransactionType.CREDIT.value:
            account.balance += transaction_data.amount
        
        db.add(new_transaction)
        db.commit()
        db.refresh(new_transaction)
        
        return TransactionRead.model_validate(new_transaction)
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create transaction: {str(e)}"
        )


def get_transaction_by_id(transaction_id: int, db: Session) -> TransactionRead:
    """
    Get transaction by ID.
    
    Args:
        transaction_id: Transaction ID
        db: Database session
        
    Returns:
        Transaction data
        
    Raises:
        HTTPException: If transaction not found
    """
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    return TransactionRead.model_validate(transaction)


def get_transactions_by_user(
    user_id: int,
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> List[TransactionRead]:
    """
    Get all transactions for a user.
    
    Args:
        user_id: User ID
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of transactions
    """
    transactions = db.query(Transaction).filter(
        Transaction.user_id == user_id
    ).order_by(Transaction.created_at.desc()).offset(skip).limit(limit).all()
    
    return [TransactionRead.model_validate(t) for t in transactions]


def get_transactions_by_account(
    account_id: int,
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> List[TransactionRead]:
    """
    Get all transactions for an account.
    
    Args:
        account_id: Account ID
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of transactions
    """
    transactions = db.query(Transaction).filter(
        Transaction.account_id == account_id
    ).order_by(Transaction.created_at.desc()).offset(skip).limit(limit).all()
    
    return [TransactionRead.model_validate(t) for t in transactions]


def get_all_transactions(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> List[TransactionRead]:
    """
    Get all transactions with pagination.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of transactions
    """
    transactions = db.query(Transaction).order_by(
        Transaction.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return [TransactionRead.model_validate(t) for t in transactions]


def filter_transactions(
    filters: TransactionFilter,
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> List[TransactionRead]:
    """
    Filter transactions based on criteria.
    
    Args:
        filters: Transaction filter criteria
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of filtered transactions
    """
    query = db.query(Transaction)
    
    # Apply filters
    if filters.user_id:
        query = query.filter(Transaction.user_id == filters.user_id)
    
    if filters.account_id:
        query = query.filter(Transaction.account_id == filters.account_id)
    
    if filters.transaction_type:
        query = query.filter(Transaction.transaction_type == filters.transaction_type)
    
    if filters.category:
        query = query.filter(Transaction.category == filters.category)
    
    if filters.status:
        query = query.filter(Transaction.status == filters.status)
    
    if filters.date_from:
        query = query.filter(Transaction.created_at >= filters.date_from)
    
    if filters.date_to:
        query = query.filter(Transaction.created_at <= filters.date_to)
    
    # Execute query
    transactions = query.order_by(
        Transaction.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return [TransactionRead.model_validate(t) for t in transactions]


def get_transaction_statistics(
    user_id: Optional[int],
    account_id: Optional[int],
    db: Session,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None
) -> TransactionStats:
    """
    Get transaction statistics.
    
    Args:
        user_id: User ID (optional)
        account_id: Account ID (optional)
        db: Database session
        date_from: Start date filter
        date_to: End date filter
        
    Returns:
        Transaction statistics
    """
    query = db.query(Transaction)
    
    # Apply filters
    if user_id:
        query = query.filter(Transaction.user_id == user_id)
    
    if account_id:
        query = query.filter(Transaction.account_id == account_id)
    
    if date_from:
        query = query.filter(Transaction.created_at >= date_from)
    
    if date_to:
        query = query.filter(Transaction.created_at <= date_to)
    
    # Get all matching transactions
    transactions = query.all()
    
    # Calculate statistics
    total_transactions = len(transactions)
    total_debits = Decimal("0.00")
    total_credits = Decimal("0.00")
    categories = {}
    
    for t in transactions:
        if t.transaction_type == TransactionType.DEBIT.value:
            total_debits += t.amount
        elif t.transaction_type == TransactionType.CREDIT.value:
            total_credits += t.amount
        
        # Count by category
        if t.category:
            categories[t.category] = categories.get(t.category, 0) + 1
    
    net_balance = total_credits - total_debits
    average_transaction = (total_credits + total_debits) / total_transactions if total_transactions > 0 else Decimal("0.00")
    
    return TransactionStats(
        total_transactions=total_transactions,
        total_debits=total_debits,
        total_credits=total_credits,
        net_balance=net_balance,
        average_transaction=average_transaction,
        categories=categories
    )


def cancel_transaction(transaction_id: int, db: Session) -> TransactionRead:
    """
    Cancel a transaction and reverse the balance change.
    
    Args:
        transaction_id: Transaction ID
        db: Database session
        
    Returns:
        Updated transaction data
        
    Raises:
        HTTPException: If transaction not found or already cancelled
    """
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id
    ).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    if transaction.status == TransactionStatus.CANCELLED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transaction is already cancelled"
        )
    
    # Get account
    account = db.query(Account).filter(Account.id == transaction.account_id).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated account not found"
        )
    
    try:
        # Reverse the balance change
        if transaction.transaction_type == TransactionType.DEBIT.value:
            account.balance += transaction.amount
        elif transaction.transaction_type == TransactionType.CREDIT.value:
            # Check if account has sufficient funds to reverse credit
            if account.balance < transaction.amount:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Insufficient funds to cancel this transaction"
                )
            account.balance -= transaction.amount
        
        # Update transaction status
        transaction.status = TransactionStatus.CANCELLED.value
        
        db.commit()
        db.refresh(transaction)
        
        return TransactionRead.model_validate(transaction)
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel transaction: {str(e)}"
        )

