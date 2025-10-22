"""
Authentication endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_database
from models import User
from schemas import UserCreate, UserUpdate, User as UserSchema, ResponseWrapper
from utils.auth import get_current_user, verify_supabase_token
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/register", response_model=ResponseWrapper)
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_database)
):
    """Register a new user"""
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already registered"
            )
        
        # Create new user
        db_user = User(
            email=user_data.email,
            name=user_data.name,
            supabase_id=user_data.supabase_id
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return ResponseWrapper(
            success=True,
            message="User registered successfully",
            data=UserSchema.from_orm(db_user)
        )
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.get("/profile", response_model=ResponseWrapper)
async def get_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user profile"""
    return ResponseWrapper(
        success=True,
        message="Profile retrieved successfully",
        data=UserSchema.from_orm(current_user)
    )

@router.put("/profile", response_model=ResponseWrapper)
async def update_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Update user profile"""
    try:
        if user_update.name:
            current_user.name = user_update.name
        
        db.commit()
        db.refresh(current_user)
        
        return ResponseWrapper(
            success=True,
            message="Profile updated successfully",
            data=UserSchema.from_orm(current_user)
        )
        
    except Exception as e:
        logger.error(f"Profile update error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile update failed"
        )

@router.post("/verify-token", response_model=ResponseWrapper)
async def verify_token(
    token: str,
    db: Session = Depends(get_database)
):
    """Verify Supabase token and get/create user"""
    try:
        user_data = await verify_supabase_token(token)
        
        # Check if user exists
        user = db.query(User).filter(User.supabase_id == user_data["sub"]).first()
        
        if not user:
            # Create new user
            user = User(
                email=user_data["email"],
                name=user_data.get("name", user_data["email"]),
                supabase_id=user_data["sub"]
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        return ResponseWrapper(
            success=True,
            message="Token verified successfully",
            data=UserSchema.from_orm(user)
        )
        
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )