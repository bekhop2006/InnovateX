"""
Product router - API endpoints for product management.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from .service import (
    create_product, get_product_by_id, get_all_products,
    search_products, update_product, delete_product,
    update_stock, get_categories
)
from .schemas import ProductCreate, ProductRead, ProductUpdate, ProductSearch

router = APIRouter()


@router.post("/products", response_model=ProductRead, status_code=201)
async def create_new_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new product.
    
    - **name**: Product name
    - **description**: Product description
    - **price**: Product price (must be positive)
    - **category**: Product category
    - **stock**: Initial stock quantity
    - **image_url**: Product image URL
    - **sku**: Stock Keeping Unit (unique)
    
    Returns created product data.
    """
    return create_product(product_data, db)


@router.get("/products", response_model=List[ProductRead])
async def get_products(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    active_only: bool = Query(False, description="Return only active products"),
    db: Session = Depends(get_db)
):
    """
    Get all products with pagination.
    
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum records to return (default: 100, max: 1000)
    - **active_only**: Return only active products (default: false)
    
    Returns list of products.
    """
    return get_all_products(db, skip, limit, active_only)


@router.get("/products/{product_id}", response_model=ProductRead)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """
    Get product by ID.
    
    - **product_id**: Product ID
    
    Returns product data.
    """
    return get_product_by_id(product_id, db)


@router.post("/products/search", response_model=List[ProductRead])
async def search_products_endpoint(
    search_params: ProductSearch,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Search products based on criteria.
    
    - **query**: Search text (searches in name and description)
    - **category**: Filter by category
    - **min_price**: Minimum price filter
    - **max_price**: Maximum price filter
    - **in_stock_only**: Return only products in stock
    
    Returns list of matching products.
    """
    return search_products(search_params, db, skip, limit)


@router.get("/products/categories/list", response_model=List[str])
async def get_product_categories(db: Session = Depends(get_db)):
    """
    Get all product categories.
    
    Returns list of unique categories.
    """
    return get_categories(db)


@router.put("/products/{product_id}", response_model=ProductRead)
async def update_product_endpoint(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db)
):
    """
    Update product details.
    
    - **product_id**: Product ID
    - **name**: New name
    - **description**: New description
    - **price**: New price
    - **category**: New category
    - **stock**: New stock quantity
    - **image_url**: New image URL
    - **sku**: New SKU
    - **is_active**: Active status (1 or 0)
    
    Returns updated product data.
    """
    return update_product(product_id, product_data, db)


@router.patch("/products/{product_id}/stock")
async def update_product_stock(
    product_id: int,
    quantity_change: int = Query(..., description="Amount to add or subtract"),
    db: Session = Depends(get_db)
):
    """
    Update product stock.
    
    - **product_id**: Product ID
    - **quantity_change**: Amount to add (positive) or subtract (negative)
    
    Returns updated product data.
    """
    return update_stock(product_id, quantity_change, db)


@router.delete("/products/{product_id}")
async def delete_product_endpoint(
    product_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a product (soft delete).
    
    - **product_id**: Product ID
    
    Sets is_active to 0 and returns success message.
    """
    return delete_product(product_id, db)


@router.get("/health")
async def product_health_check():
    """Health check for product service."""
    return {"status": "healthy", "service": "product"}

