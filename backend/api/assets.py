"""
Asset management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_database
from models import User, Asset
from schemas import (
    AssetCreate, AssetUpdate, Asset as AssetSchema, 
    ResponseWrapper, PaginatedResponse
)
from utils.auth import get_current_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=ResponseWrapper)
async def create_asset(
    asset_data: AssetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Create a new asset (property or vehicle)"""
    try:
        db_asset = Asset(
            user_id=current_user.id,
            type=asset_data.type,
            name=asset_data.name,
            details_json=asset_data.details_json
        )
        db.add(db_asset)
        db.commit()
        db.refresh(db_asset)
        
        return ResponseWrapper(
            success=True,
            message="Asset created successfully",
            data=AssetSchema.from_orm(db_asset)
        )
        
    except Exception as e:
        logger.error(f"Asset creation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Asset creation failed"
        )

@router.get("/", response_model=ResponseWrapper)
async def get_assets(
    asset_type: Optional[str] = None,
    page: int = 1,
    per_page: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Get user's assets with optional filtering and pagination"""
    try:
        query = db.query(Asset).filter(Asset.user_id == current_user.id)
        
        if asset_type:
            query = query.filter(Asset.type == asset_type)
        
        total = query.count()
        assets = query.offset((page - 1) * per_page).limit(per_page).all()
        
        return ResponseWrapper(
            success=True,
            message="Assets retrieved successfully",
            data=PaginatedResponse(
                items=[AssetSchema.from_orm(asset) for asset in assets],
                total=total,
                page=page,
                per_page=per_page,
                pages=(total + per_page - 1) // per_page
            )
        )
        
    except Exception as e:
        logger.error(f"Assets retrieval error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve assets"
        )

@router.get("/{asset_id}", response_model=ResponseWrapper)
async def get_asset(
    asset_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Get specific asset by ID"""
    try:
        asset = db.query(Asset).filter(
            Asset.id == asset_id,
            Asset.user_id == current_user.id
        ).first()
        
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset not found"
            )
        
        return ResponseWrapper(
            success=True,
            message="Asset retrieved successfully",
            data=AssetSchema.from_orm(asset)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Asset retrieval error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve asset"
        )

@router.put("/{asset_id}", response_model=ResponseWrapper)
async def update_asset(
    asset_id: int,
    asset_update: AssetUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Update asset"""
    try:
        asset = db.query(Asset).filter(
            Asset.id == asset_id,
            Asset.user_id == current_user.id
        ).first()
        
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset not found"
            )
        
        if asset_update.name:
            asset.name = asset_update.name
        if asset_update.details_json is not None:
            asset.details_json = asset_update.details_json
        
        db.commit()
        db.refresh(asset)
        
        return ResponseWrapper(
            success=True,
            message="Asset updated successfully",
            data=AssetSchema.from_orm(asset)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Asset update error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Asset update failed"
        )

@router.delete("/{asset_id}", response_model=ResponseWrapper)
async def delete_asset(
    asset_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Delete asset"""
    try:
        asset = db.query(Asset).filter(
            Asset.id == asset_id,
            Asset.user_id == current_user.id
        ).first()
        
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset not found"
            )
        
        db.delete(asset)
        db.commit()
        
        return ResponseWrapper(
            success=True,
            message="Asset deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Asset deletion error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Asset deletion failed"
        )