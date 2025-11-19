from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from ....core.database import get_db
from ....core.security import get_current_user
from ....models.user import User
from ....models.merchant import Merchant
from ....models.product import Product
from ....schemas.product import ProductCreate, ProductResponse, ProductUpdate, ProductListResponse
from ....services.cloudinary_service import cloudinary_service

router = APIRouter()


@router.post("/", response_model=ProductResponse)
async def create_product(
        product_data: ProductCreate,
        image: Optional[UploadFile] = File(None),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    # Get merchant for current user
    merchant = db.query(Merchant).filter(Merchant.owner_id == current_user.id).first()
    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Merchant account not found"
        )

    # Check if user owns the merchant they're trying to add product to
    if product_data.merchant_id != merchant.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to add products to this merchant"
        )

    # Check if SKU already exists
    existing_product = db.query(Product).filter(
        Product.sku == product_data.sku,
        Product.merchant_id == merchant.id
    ).first()

    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product with this SKU already exists"
        )

    # Handle image upload
    image_url = None
    cloudinary_public_id = None

    if image:
        upload_result = cloudinary_service.upload_image(image.file)
        image_url = upload_result["url"]
        cloudinary_public_id = upload_result["public_id"]

    # Create product
    db_product = Product(
        **product_data.dict(),
        image_url=image_url,
        cloudinary_public_id=cloudinary_public_id
    )

    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    return db_product


@router.get("/", response_model=ProductListResponse)
async def get_products(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=100),
        merchant_id: Optional[int] = None,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    # Get merchant for current user
    merchant = db.query(Merchant).filter(Merchant.owner_id == current_user.id).first()
    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Merchant account not found"
        )

    # Base query - only show products for user's merchant
    query = db.query(Product).filter(Product.merchant_id == merchant.id)

    # If merchant_id is specified and user is superuser, allow viewing other merchants
    if merchant_id and current_user.is_superuser:
        query = db.query(Product).filter(Product.merchant_id == merchant_id)
    elif merchant_id and merchant_id != merchant.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view products for this merchant"
        )

    total = query.count()
    products = query.offset(skip).limit(limit).all()

    return ProductListResponse(
        items=products,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
        product_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    # Check authorization
    merchant = db.query(Merchant).filter(Merchant.owner_id == current_user.id).first()
    if not current_user.is_superuser and product.merchant_id != merchant.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this product"
        )

    return product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
        product_id: int,
        product_data: ProductUpdate,
        image: Optional[UploadFile] = File(None),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    # Check authorization
    merchant = db.query(Merchant).filter(Merchant.owner_id == current_user.id).first()
    if not current_user.is_superuser and product.merchant_id != merchant.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this product"
        )

    # Handle image update
    if image:
        if product.cloudinary_public_id:
            # Update existing image
            upload_result = cloudinary_service.update_image(
                product.cloudinary_public_id,
                image.file
            )
        else:
            # Upload new image
            upload_result = cloudinary_service.upload_image(image.file)

        product.image_url = upload_result["url"]
        product.cloudinary_public_id = upload_result["public_id"]

    # Update product fields
    for field, value in product_data.dict(exclude_unset=True).items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)

    return product


@router.delete("/{product_id}")
async def delete_product(
        product_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    # Check authorization
    merchant = db.query(Merchant).filter(Merchant.owner_id == current_user.id).first()
    if not current_user.is_superuser and product.merchant_id != merchant.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this product"
        )

    # Delete image from Cloudinary if exists
    if product.cloudinary_public_id:
        cloudinary_service.delete_image(product.cloudinary_public_id)

    db.delete(product)
    db.commit()

    return {"message": "Product deleted successfully"}
