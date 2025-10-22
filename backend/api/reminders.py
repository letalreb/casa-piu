"""
Reminders management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_database
from models import User, Reminder
from schemas import ReminderCreate, Reminder as ReminderSchema, ResponseWrapper, PaginatedResponse
from utils.auth import get_current_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=ResponseWrapper)
async def get_reminders(
    page: int = 1,
    per_page: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Get user's reminders"""
    try:
        # Get user's assets first
        from models import Asset
        user_assets = db.query(Asset).filter(Asset.user_id == current_user.id).all()
        asset_ids = [asset.id for asset in user_assets]
        
        query = db.query(Reminder).filter(Reminder.asset_id.in_(asset_ids))
        total = query.count()
        reminders = query.offset((page - 1) * per_page).limit(per_page).all()
        
        return ResponseWrapper(
            success=True,
            message="Reminders retrieved successfully",
            data=PaginatedResponse(
                items=[ReminderSchema.from_orm(reminder) for reminder in reminders],
                total=total,
                page=page,
                per_page=per_page,
                pages=(total + per_page - 1) // per_page
            )
        )
    except Exception as e:
        logger.error(f"Reminders retrieval error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve reminders"
        )

@router.post("/", response_model=ResponseWrapper)
async def create_reminder(
    reminder_data: ReminderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Create a new reminder"""
    try:
        from models import Asset
        # Verify asset belongs to user
        asset = db.query(Asset).filter(
            Asset.id == reminder_data.asset_id,
            Asset.user_id == current_user.id
        ).first()
        
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset not found"
            )
        
        db_reminder = Reminder(
            asset_id=reminder_data.asset_id,
            type=reminder_data.type,
            date=reminder_data.date,
            message=reminder_data.message
        )
        db.add(db_reminder)
        db.commit()
        db.refresh(db_reminder)
        
        return ResponseWrapper(
            success=True,
            message="Reminder created successfully",
            data=ReminderSchema.from_orm(db_reminder)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Reminder creation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Reminder creation failed"
        )

@router.post("/run", response_model=ResponseWrapper)
async def run_reminders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Manually trigger reminder check"""
    try:
        from utils.scheduler import SchedulerService
        scheduler = SchedulerService()
        await scheduler.check_reminders()
        
        return ResponseWrapper(
            success=True,
            message="Reminders checked successfully"
        )
    except Exception as e:
        logger.error(f"Reminder run error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to run reminders"
        )