"""
Product service - business logic for product management.
"""
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException, status
from typing import List, Optional
from decimal import Decimal

from models.product import Product
from .schemas import ProductCreate, ProductRead, ProductUpdate, ProductSearch


def create_product(product_data: ProductCreate, db: Session) -> ProductRead:
    """
    Create a new product.
    
    Args:
        product_data: Product creation data
        db: Database session
        
    Returns:
        Created product data
        
    Raises:
        HTTPException: If SKU already exists
    """
    # Check if SKU already exists
    if product_data.sku:
        existing = db.query(Product).filter(Product.sku == product_data.sku).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product with this SKU already exists"
            )
    
    try:
        new_product = Product(
            name=product_data.name,
            description=product_data.description,
            price=product_data.price,
            category=product_data.category,
            stock=product_data.stock,
            image_url=product_data.image_url,
            sku=product_data.sku,
            is_active=1
        )
        
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
        
        return ProductRead.model_validate(new_product)
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create product: {str(e)}"
        )


def get_product_by_id(product_id: int, db: Session) -> ProductRead:
    """
    Get product by ID.
    
    Args:
        product_id: Product ID
        db: Database session
        
    Returns:
        Product data
        
    Raises:
        HTTPException: If product not found
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return ProductRead.model_validate(product)


def get_all_products(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False
) -> List[ProductRead]:
    """
    Get all products with pagination.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        active_only: Return only active products
        
    Returns:
        List of products
    """
    query = db.query(Product)
    
    if active_only:
        query = query.filter(Product.is_active == 1)
    
    products = query.offset(skip).limit(limit).all()
    
    return [ProductRead.model_validate(p) for p in products]


def search_products(
    search_params: ProductSearch,
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> List[ProductRead]:
    """
    Search products based on criteria.
    
    Args:
        search_params: Search parameters
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of matching products
    """
    query = db.query(Product).filter(Product.is_active == 1)
    
    # Text search in name and description
    if search_params.query:
        search_term = f"%{search_params.query}%"
        query = query.filter(
            or_(
                Product.name.ilike(search_term),
                Product.description.ilike(search_term)
            )
        )
    
    # Category filter
    if search_params.category:
        query = query.filter(Product.category == search_params.category)
    
    # Price range filter
    if search_params.min_price is not None:
        query = query.filter(Product.price >= search_params.min_price)
    
    if search_params.max_price is not None:
        query = query.filter(Product.price <= search_params.max_price)
    
    # Stock filter
    if search_params.in_stock_only:
        query = query.filter(Product.stock > 0)
    
    products = query.offset(skip).limit(limit).all()
    
    return [ProductRead.model_validate(p) for p in products]


def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session
) -> ProductRead:
    """
    Update product details.
    
    Args:
        product_id: Product ID
        product_data: Updated product data
        db: Database session
        
    Returns:
        Updated product data
        
    Raises:
        HTTPException: If product not found
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Update fields
    if product_data.name is not None:
        product.name = product_data.name
    if product_data.description is not None:
        product.description = product_data.description
    if product_data.price is not None:
        product.price = product_data.price
    if product_data.category is not None:
        product.category = product_data.category
    if product_data.stock is not None:
        product.stock = product_data.stock
    if product_data.image_url is not None:
        product.image_url = product_data.image_url
    if product_data.sku is not None:
        # Check if new SKU already exists
        existing = db.query(Product).filter(
            Product.sku == product_data.sku,
            Product.id != product_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product with this SKU already exists"
            )
        product.sku = product_data.sku
    if product_data.is_active is not None:
        product.is_active = product_data.is_active
    
    try:
        db.commit()
        db.refresh(product)
        return ProductRead.model_validate(product)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update product: {str(e)}"
        )


def delete_product(product_id: int, db: Session) -> dict:
    """
    Delete a product (soft delete by setting is_active to 0).
    
    Args:
        product_id: Product ID
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If product not found
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Soft delete
    product.is_active = 0
    
    try:
        db.commit()
        return {"message": "Product deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete product: {str(e)}"
        )


def update_stock(product_id: int, quantity_change: int, db: Session) -> ProductRead:
    """
    Update product stock.
    
    Args:
        product_id: Product ID
        quantity_change: Amount to add (positive) or subtract (negative)
        db: Database session
        
    Returns:
        Updated product data
        
    Raises:
        HTTPException: If product not found or insufficient stock
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    new_stock = product.stock + quantity_change
    
    if new_stock < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient stock"
        )
    
    product.stock = new_stock
    
    try:
        db.commit()
        db.refresh(product)
        return ProductRead.model_validate(product)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update stock: {str(e)}"
        )


def get_categories(db: Session) -> List[str]:
    """
    Get all product categories.
    
    Args:
        db: Database session
        
    Returns:
        List of unique categories
    """
    categories = db.query(Product.category).filter(
        Product.category.isnot(None),
        Product.is_active == 1
    ).distinct().all()
    
    return [cat[0] for cat in categories if cat[0]]

