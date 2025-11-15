"""
Cart service - business logic for shopping cart management.
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List
from decimal import Decimal

from models.cart import Cart
from models.product import Product
from models.user import User
from models.account import Account
from models.transaction import Transaction, TransactionType
from .schemas import (
    CartItemCreate, CartItemRead, CartItemWithProduct,
    CartSummary, CartItemUpdate, CheckoutRequest
)


def add_to_cart(cart_data: CartItemCreate, db: Session) -> CartItemRead:
    """
    Add item to cart or update quantity if already exists.
    
    Args:
        cart_data: Cart item data
        db: Database session
        
    Returns:
        Cart item data
        
    Raises:
        HTTPException: If user/product not found or insufficient stock
    """
    # Verify user exists
    user = db.query(User).filter(User.id == cart_data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify product exists and is active
    product = db.query(Product).filter(
        Product.id == cart_data.product_id,
        Product.is_active == 1
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found or inactive"
        )
    
    # Check stock availability
    if product.stock < cart_data.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient stock. Only {product.stock} items available."
        )
    
    # Check if item already in cart
    existing_item = db.query(Cart).filter(
        Cart.user_id == cart_data.user_id,
        Cart.product_id == cart_data.product_id
    ).first()
    
    try:
        if existing_item:
            # Update quantity
            new_quantity = existing_item.quantity + cart_data.quantity
            
            # Check stock for new quantity
            if product.stock < new_quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient stock. Only {product.stock} items available."
                )
            
            existing_item.quantity = new_quantity
            db.commit()
            db.refresh(existing_item)
            return CartItemRead.model_validate(existing_item)
        else:
            # Create new cart item
            new_item = Cart(
                user_id=cart_data.user_id,
                product_id=cart_data.product_id,
                quantity=cart_data.quantity
            )
            
            db.add(new_item)
            db.commit()
            db.refresh(new_item)
            return CartItemRead.model_validate(new_item)
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add item to cart: {str(e)}"
        )


def get_cart_by_user(user_id: int, db: Session) -> CartSummary:
    """
    Get cart items for a user with product details.
    
    Args:
        user_id: User ID
        db: Database session
        
    Returns:
        Cart summary with items
    """
    # Get cart items with product details
    cart_items = db.query(Cart).filter(Cart.user_id == user_id).all()
    
    items_with_products = []
    total_price = Decimal("0.00")
    
    for cart_item in cart_items:
        product = db.query(Product).filter(Product.id == cart_item.product_id).first()
        
        if product:
            item_total = product.price * cart_item.quantity
            total_price += item_total
            
            items_with_products.append(
                CartItemWithProduct(
                    cart_id=cart_item.id,
                    product_id=product.id,
                    product_name=product.name,
                    product_price=product.price,
                    product_image=product.image_url,
                    quantity=cart_item.quantity,
                    item_total=item_total,
                    in_stock=product.stock >= cart_item.quantity
                )
            )
    
    return CartSummary(
        user_id=user_id,
        items=items_with_products,
        total_items=len(items_with_products),
        total_price=total_price
    )


def update_cart_item(
    cart_id: int,
    update_data: CartItemUpdate,
    db: Session
) -> CartItemRead:
    """
    Update cart item quantity.
    
    Args:
        cart_id: Cart item ID
        update_data: Update data
        db: Database session
        
    Returns:
        Updated cart item
        
    Raises:
        HTTPException: If item not found or insufficient stock
    """
    cart_item = db.query(Cart).filter(Cart.id == cart_id).first()
    
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )
    
    # If quantity is 0, delete the item
    if update_data.quantity == 0:
        db.delete(cart_item)
        db.commit()
        return CartItemRead.model_validate(cart_item)
    
    # Check stock availability
    product = db.query(Product).filter(Product.id == cart_item.product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    if product.stock < update_data.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient stock. Only {product.stock} items available."
        )
    
    # Update quantity
    cart_item.quantity = update_data.quantity
    
    try:
        db.commit()
        db.refresh(cart_item)
        return CartItemRead.model_validate(cart_item)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update cart item: {str(e)}"
        )


def remove_from_cart(cart_id: int, db: Session) -> dict:
    """
    Remove item from cart.
    
    Args:
        cart_id: Cart item ID
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If item not found
    """
    cart_item = db.query(Cart).filter(Cart.id == cart_id).first()
    
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )
    
    try:
        db.delete(cart_item)
        db.commit()
        return {"message": "Item removed from cart"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove item: {str(e)}"
        )


def clear_cart(user_id: int, db: Session) -> dict:
    """
    Clear all items from user's cart.
    
    Args:
        user_id: User ID
        db: Database session
        
    Returns:
        Success message
    """
    try:
        db.query(Cart).filter(Cart.user_id == user_id).delete()
        db.commit()
        return {"message": "Cart cleared"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear cart: {str(e)}"
        )


def checkout(checkout_data: CheckoutRequest, db: Session) -> dict:
    """
    Process checkout: create transaction and clear cart.
    
    Args:
        checkout_data: Checkout request data
        db: Database session
        
    Returns:
        Checkout result
        
    Raises:
        HTTPException: If cart is empty, insufficient funds, or insufficient stock
    """
    # Get cart items
    cart_items = db.query(Cart).filter(Cart.user_id == checkout_data.user_id).all()
    
    if not cart_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart is empty"
        )
    
    # Get account
    account = db.query(Account).filter(
        Account.id == checkout_data.account_id,
        Account.user_id == checkout_data.user_id
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    # Calculate total and check stock
    total_amount = Decimal("0.00")
    items_to_purchase = []
    
    for cart_item in cart_items:
        product = db.query(Product).filter(Product.id == cart_item.product_id).first()
        
        if not product or product.is_active != 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product {cart_item.product_id} not available"
            )
        
        if product.stock < cart_item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for {product.name}. Only {product.stock} available."
            )
        
        item_total = product.price * cart_item.quantity
        total_amount += item_total
        
        items_to_purchase.append({
            "product": product,
            "quantity": cart_item.quantity,
            "price": product.price,
            "total": item_total
        })
    
    # Check if account has sufficient balance
    if account.balance < total_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient funds. Required: {total_amount}, Available: {account.balance}"
        )
    
    try:
        # Deduct balance
        account.balance -= total_amount
        
        # Create transaction
        transaction = Transaction(
            user_id=checkout_data.user_id,
            account_id=checkout_data.account_id,
            amount=total_amount,
            transaction_type=TransactionType.DEBIT.value,
            description="Purchase from shop",
            category="shopping",
            status="completed"
        )
        db.add(transaction)
        
        # Update product stocks
        for item in items_to_purchase:
            item["product"].stock -= item["quantity"]
        
        # Clear cart
        db.query(Cart).filter(Cart.user_id == checkout_data.user_id).delete()
        
        db.commit()
        
        return {
            "message": "Checkout successful",
            "transaction_id": transaction.id,
            "total_amount": float(total_amount),
            "items_purchased": len(items_to_purchase),
            "new_balance": float(account.balance)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Checkout failed: {str(e)}"
        )

