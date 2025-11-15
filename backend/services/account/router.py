"""
Account router - API endpoints for account management.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from .service import (
    create_account, get_account_by_id, get_accounts_by_user,
    get_all_accounts, update_account, update_balance,
    transfer_funds, delete_account
)
from .schemas import (
    AccountCreate, AccountRead, AccountUpdate,
    BalanceUpdate, TransferRequest
)

router = APIRouter()


@router.post("/accounts", response_model=AccountRead, status_code=201)
async def create_new_account(
    account_data: AccountCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new account.
    
    - **user_id**: User ID who owns the account
    - **account_type**: Account type (checking, savings, credit)
    - **currency**: Account currency (default: USD)
    - **initial_balance**: Initial balance (default: 0.00)
    
    Returns created account data.
    """
    return create_account(account_data, db)


@router.get("/accounts", response_model=List[AccountRead])
async def get_accounts(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """
    Get all accounts with pagination.
    
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum records to return (default: 100, max: 1000)
    
    Returns list of accounts.
    """
    return get_all_accounts(db, skip, limit)


@router.get("/accounts/{account_id}", response_model=AccountRead)
async def get_account(
    account_id: int,
    db: Session = Depends(get_db)
):
    """
    Get account by ID.
    
    - **account_id**: Account ID
    
    Returns account data.
    """
    return get_account_by_id(account_id, db)


@router.get("/accounts/user/{user_id}", response_model=List[AccountRead])
async def get_user_accounts(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all accounts for a specific user.
    
    - **user_id**: User ID
    
    Returns list of user's accounts.
    """
    return get_accounts_by_user(user_id, db)


@router.put("/accounts/{account_id}", response_model=AccountRead)
async def update_account_details(
    account_id: int,
    account_data: AccountUpdate,
    db: Session = Depends(get_db)
):
    """
    Update account details.
    
    - **account_id**: Account ID
    - **status**: New status (active, blocked, closed)
    - **currency**: New currency
    
    Returns updated account data.
    """
    return update_account(account_id, account_data, db)


@router.patch("/accounts/{account_id}/balance", response_model=AccountRead)
async def update_account_balance(
    account_id: int,
    balance_data: BalanceUpdate,
    db: Session = Depends(get_db)
):
    """
    Update account balance.
    
    - **account_id**: Account ID
    - **amount**: Amount to add (positive) or subtract (negative)
    - **description**: Description of the balance change
    
    Creates a transaction record and returns updated account data.
    """
    return update_balance(account_id, balance_data, db)


@router.post("/accounts/transfer")
async def transfer_between_accounts(
    transfer_data: TransferRequest,
    db: Session = Depends(get_db)
):
    """
    Transfer funds between accounts.
    
    - **from_account_id**: Source account ID
    - **to_account_id**: Destination account ID
    - **amount**: Amount to transfer (must be positive)
    - **description**: Transfer description
    
    Returns transfer result with transaction IDs.
    """
    return transfer_funds(transfer_data, db)


@router.delete("/accounts/{account_id}")
async def delete_account_endpoint(
    account_id: int,
    db: Session = Depends(get_db)
):
    """
    Soft delete an account.
    
    - **account_id**: Account ID
    
    Account must have zero balance to be deleted.
    Returns success message.
    """
    return delete_account(account_id, db)


@router.get("/health")
async def account_health_check():
    """Health check for account service."""
    return {"status": "healthy", "service": "account"}

