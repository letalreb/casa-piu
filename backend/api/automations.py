"""
Automations management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_database
from models import User, Asset, Automation
from schemas import AutomationCreate, AutomationUpdate, Automation as AutomationSchema, ResponseWrapper
from utils.auth import get_current_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=ResponseWrapper)
async def create_automation(
    automation_data: AutomationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Create automation settings for an asset"""
    try:
        # Verify asset belongs to user
        asset = db.query(Asset).filter(
            Asset.id == automation_data.asset_id,
            Asset.user_id == current_user.id
        ).first()
        
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset not found"
            )
        
        # Check if automation already exists
        existing = db.query(Automation).filter(
            Automation.asset_id == automation_data.asset_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Automation already exists for this asset"
            )
        
        db_automation = Automation(
            asset_id=automation_data.asset_id,
            imu_calc=automation_data.imu_calc,
            f24_gen=automation_data.f24_gen,
            ocr=automation_data.ocr,
            ai_suggestions=automation_data.ai_suggestions
        )
        db.add(db_automation)
        db.commit()
        db.refresh(db_automation)
        
        return ResponseWrapper(
            success=True,
            message="Automation created successfully",
            data=AutomationSchema.from_orm(db_automation)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Automation creation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Automation creation failed"
        )

@router.get("/{asset_id}", response_model=ResponseWrapper)
async def get_automation(
    asset_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Get automation settings for an asset"""
    try:
        # Verify asset belongs to user
        asset = db.query(Asset).filter(
            Asset.id == asset_id,
            Asset.user_id == current_user.id
        ).first()
        
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset not found"
            )
        
        automation = db.query(Automation).filter(
            Automation.asset_id == asset_id
        ).first()
        
        if not automation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Automation not found"
            )
        
        return ResponseWrapper(
            success=True,
            message="Automation retrieved successfully",
            data=AutomationSchema.from_orm(automation)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Automation retrieval error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve automation"
        )

@router.put("/{automation_id}", response_model=ResponseWrapper)
async def update_automation(
    automation_id: int,
    automation_update: AutomationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Update automation settings"""
    try:
        automation = db.query(Automation).filter(
            Automation.id == automation_id
        ).first()
        
        if not automation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Automation not found"
            )
        
        # Verify asset belongs to user
        asset = db.query(Asset).filter(
            Asset.id == automation.asset_id,
            Asset.user_id == current_user.id
        ).first()
        
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized"
            )
        
        update_data = automation_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(automation, field, value)
        
        db.commit()
        db.refresh(automation)
        
        return ResponseWrapper(
            success=True,
            message="Automation updated successfully",
            data=AutomationSchema.from_orm(automation)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Automation update error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Automation update failed"
        )