"""
Cart router - API endpoints for shopping cart management.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from .service import (
    add_to_cart, get_cart_by_user, update_cart_item,
    remove_from_cart, clear_cart, checkout
)
from .schemas import (
    CartItemCreate, CartItemRead, CartSummary,
    CartItemUpdate, CheckoutRequest
)

router = APIRouter()


@router.post("/cart", response_model=CartItemRead, status_code=201)
async def add_item_to_cart(
    cart_data: CartItemCreate,
    db: Session = Depends(get_db)
):
    """
    Add item to cart.
    
    - **user_id**: User ID
    - **product_id**: Product ID to add
    - **quantity**: Quantity (default: 1)
    
    If item already exists in cart, quantity will be incremented.
    Returns cart item data.
    """
    return add_to_cart(cart_data, db)


@router.get("/cart/user/{user_id}", response_model=CartSummary)
async def get_user_cart(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get cart for a specific user.
    
    - **user_id**: User ID
    
    Returns cart summary with all items and total price.
    """
    return get_cart_by_user(user_id, db)


@router.put("/cart/{cart_id}", response_model=CartItemRead)
async def update_cart_item_quantity(
    cart_id: int,
    update_data: CartItemUpdate,
    db: Session = Depends(get_db)
):
    """
    Update cart item quantity.
    
    - **cart_id**: Cart item ID
    - **quantity**: New quantity (set to 0 to remove)
    
    Returns updated cart item.
    """
    return update_cart_item(cart_id, update_data, db)


@router.delete("/cart/{cart_id}")
async def remove_cart_item(
    cart_id: int,
    db: Session = Depends(get_db)
):
    """
    Remove item from cart.
    
    - **cart_id**: Cart item ID
    
    Returns success message.
    """
    return remove_from_cart(cart_id, db)


@router.delete("/cart/user/{user_id}/clear")
async def clear_user_cart(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Clear all items from user's cart.
    
    - **user_id**: User ID
    
    Returns success message.
    """
    return clear_cart(user_id, db)


@router.post("/cart/checkout")
async def checkout_cart(
    checkout_data: CheckoutRequest,
    db: Session = Depends(get_db)
):
    """
    Process checkout and complete purchase.
    
    - **user_id**: User ID
    - **account_id**: Account ID for payment
    
    Steps:
    1. Validates cart items and stock
    2. Checks account balance
    3. Creates debit transaction
    4. Updates product stocks
    5. Clears cart
    
    Returns checkout result with transaction details.
    """
    return checkout(checkout_data, db)


@router.get("/health")
async def cart_health_check():
    """Health check for cart service."""
    return {"status": "healthy", "service": "cart"}

