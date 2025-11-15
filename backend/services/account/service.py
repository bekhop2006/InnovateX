"""
Account service - business logic for account management.
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import List
from decimal import Decimal

from models.account import Account, AccountType, AccountStatus
from models.user import User
from models.transaction import Transaction, TransactionType
from .schemas import AccountCreate, AccountRead, AccountUpdate, BalanceUpdate, TransferRequest


def create_account(account_data: AccountCreate, db: Session) -> AccountRead:
    """
    Create a new account for a user.
    
    Args:
        account_data: Account creation data
        db: Database session
        
    Returns:
        Created account data
        
    Raises:
        HTTPException: If user doesn't exist or invalid account type
    """
    # Verify user exists
    user = db.query(User).filter(User.id == account_data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Validate account type
    valid_types = [t.value for t in AccountType]
    if account_data.account_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid account type. Must be one of: {', '.join(valid_types)}"
        )
    
    try:
        # Create account
        new_account = Account(
            user_id=account_data.user_id,
            account_type=account_data.account_type,
            balance=account_data.initial_balance or Decimal("0.00"),
            currency=account_data.currency,
            status=AccountStatus.ACTIVE.value
        )
        
        db.add(new_account)
        db.commit()
        db.refresh(new_account)
        
        return AccountRead.model_validate(new_account)
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create account: {str(e)}"
        )


def get_account_by_id(account_id: int, db: Session) -> AccountRead:
    """
    Get account by ID.
    
    Args:
        account_id: Account ID
        db: Database session
        
    Returns:
        Account data
        
    Raises:
        HTTPException: If account not found
    """
    account = db.query(Account).filter(
        Account.id == account_id,
        Account.deleted_at.is_(None)
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    return AccountRead.model_validate(account)


def get_accounts_by_user(user_id: int, db: Session) -> List[AccountRead]:
    """
    Get all accounts for a user.
    
    Args:
        user_id: User ID
        db: Database session
        
    Returns:
        List of accounts
    """
    accounts = db.query(Account).filter(
        Account.user_id == user_id,
        Account.deleted_at.is_(None)
    ).all()
    
    return [AccountRead.model_validate(account) for account in accounts]


def get_all_accounts(db: Session, skip: int = 0, limit: int = 100) -> List[AccountRead]:
    """
    Get all accounts with pagination.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of accounts
    """
    accounts = db.query(Account).filter(
        Account.deleted_at.is_(None)
    ).offset(skip).limit(limit).all()
    
    return [AccountRead.model_validate(account) for account in accounts]


def update_account(account_id: int, account_data: AccountUpdate, db: Session) -> AccountRead:
    """
    Update account details.
    
    Args:
        account_id: Account ID
        account_data: Updated account data
        db: Database session
        
    Returns:
        Updated account data
        
    Raises:
        HTTPException: If account not found or invalid status
    """
    account = db.query(Account).filter(
        Account.id == account_id,
        Account.deleted_at.is_(None)
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    # Update status if provided
    if account_data.status is not None:
        valid_statuses = [s.value for s in AccountStatus]
        if account_data.status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
        account.status = account_data.status
    
    # Update currency if provided
    if account_data.currency is not None:
        account.currency = account_data.currency
    
    try:
        db.commit()
        db.refresh(account)
        return AccountRead.model_validate(account)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update account: {str(e)}"
        )


def update_balance(account_id: int, balance_data: BalanceUpdate, db: Session) -> AccountRead:
    """
    Update account balance and create transaction record.
    
    Args:
        account_id: Account ID
        balance_data: Balance update data
        db: Database session
        
    Returns:
        Updated account data
        
    Raises:
        HTTPException: If account not found or insufficient funds
    """
    account = db.query(Account).filter(
        Account.id == account_id,
        Account.deleted_at.is_(None)
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    # Check if account is active
    if account.status != AccountStatus.ACTIVE.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Account is {account.status}. Cannot update balance."
        )
    
    # Calculate new balance
    new_balance = account.balance + balance_data.amount
    
    # Check for sufficient funds (prevent negative balance for non-credit accounts)
    if new_balance < 0 and account.account_type != AccountType.CREDIT.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient funds"
        )
    
    # Update balance
    account.balance = new_balance
    
    # Create transaction record
    transaction_type = TransactionType.CREDIT.value if balance_data.amount > 0 else TransactionType.DEBIT.value
    
    transaction = Transaction(
        user_id=account.user_id,
        account_id=account_id,
        amount=abs(balance_data.amount),
        transaction_type=transaction_type,
        description=balance_data.description or f"Balance {transaction_type}",
        status="completed"
    )
    
    try:
        db.add(transaction)
        db.commit()
        db.refresh(account)
        return AccountRead.model_validate(account)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update balance: {str(e)}"
        )


def transfer_funds(transfer_data: TransferRequest, db: Session) -> dict:
    """
    Transfer funds between accounts.
    
    Args:
        transfer_data: Transfer request data
        db: Database session
        
    Returns:
        Transfer result with transaction IDs
        
    Raises:
        HTTPException: If accounts not found, insufficient funds, or currency mismatch
    """
    # Get source account
    from_account = db.query(Account).filter(
        Account.id == transfer_data.from_account_id,
        Account.deleted_at.is_(None)
    ).first()
    
    if not from_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source account not found"
        )
    
    # Get destination account
    to_account = db.query(Account).filter(
        Account.id == transfer_data.to_account_id,
        Account.deleted_at.is_(None)
    ).first()
    
    if not to_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Destination account not found"
        )
    
    # Check if both accounts are active
    if from_account.status != AccountStatus.ACTIVE.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Source account is not active"
        )
    
    if to_account.status != AccountStatus.ACTIVE.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Destination account is not active"
        )
    
    # Check currency match
    if from_account.currency != to_account.currency:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Currency mismatch. Both accounts must have the same currency."
        )
    
    # Check sufficient funds
    if from_account.balance < transfer_data.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient funds in source account"
        )
    
    try:
        # Update balances
        from_account.balance -= transfer_data.amount
        to_account.balance += transfer_data.amount
        
        # Create debit transaction for source account
        debit_transaction = Transaction(
            user_id=from_account.user_id,
            account_id=from_account.id,
            amount=transfer_data.amount,
            transaction_type=TransactionType.TRANSFER.value,
            description=transfer_data.description or f"Transfer to account {to_account.id}",
            status="completed"
        )
        db.add(debit_transaction)
        db.flush()  # Get transaction ID
        
        # Create credit transaction for destination account
        credit_transaction = Transaction(
            user_id=to_account.user_id,
            account_id=to_account.id,
            amount=transfer_data.amount,
            transaction_type=TransactionType.TRANSFER.value,
            description=transfer_data.description or f"Transfer from account {from_account.id}",
            status="completed",
            reference_transaction_id=debit_transaction.id
        )
        db.add(credit_transaction)
        
        # Link transactions
        debit_transaction.reference_transaction_id = credit_transaction.id
        
        db.commit()
        
        return {
            "message": "Transfer completed successfully",
            "from_account_id": from_account.id,
            "to_account_id": to_account.id,
            "amount": float(transfer_data.amount),
            "currency": from_account.currency,
            "debit_transaction_id": debit_transaction.id,
            "credit_transaction_id": credit_transaction.id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to transfer funds: {str(e)}"
        )


def delete_account(account_id: int, db: Session) -> dict:
    """
    Soft delete an account.
    
    Args:
        account_id: Account ID
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If account not found or has non-zero balance
    """
    from datetime import datetime
    
    account = db.query(Account).filter(
        Account.id == account_id,
        Account.deleted_at.is_(None)
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    # Check if account has zero balance
    if account.balance != 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete account with non-zero balance. Please withdraw or transfer all funds first."
        )
    
    # Soft delete
    account.deleted_at = datetime.utcnow()
    account.status = AccountStatus.CLOSED.value
    
    try:
        db.commit()
        return {"message": "Account deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete account: {str(e)}"
        )

