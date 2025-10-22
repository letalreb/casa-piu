"""
Expenses management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from database import get_database
from models import User, Expense
from schemas import ExpenseCreate, ExpenseUpdate, Expense as ExpenseSchema, ResponseWrapper, PaginatedResponse
from utils.auth import get_current_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=ResponseWrapper)
async def create_expense(
    expense_data: ExpenseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Create a new expense"""
    try:
        db_expense = Expense(
            user_id=current_user.id,
            asset_id=expense_data.asset_id,
            category=expense_data.category,
            amount=expense_data.amount,
            due_date=expense_data.due_date,
            status=expense_data.status,
            description=expense_data.description
        )
        db.add(db_expense)
        db.commit()
        db.refresh(db_expense)
        
        return ResponseWrapper(
            success=True,
            message="Expense created successfully",
            data=ExpenseSchema.from_orm(db_expense)
        )
    except Exception as e:
        logger.error(f"Expense creation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Expense creation failed"
        )

@router.get("/", response_model=ResponseWrapper)
async def get_expenses(
    category: Optional[str] = None,
    status_filter: Optional[str] = None,
    page: int = 1,
    per_page: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Get user's expenses with optional filtering"""
    try:
        query = db.query(Expense).filter(Expense.user_id == current_user.id)
        
        if category:
            query = query.filter(Expense.category == category)
        if status_filter:
            query = query.filter(Expense.status == status_filter)
        
        total = query.count()
        expenses = query.offset((page - 1) * per_page).limit(per_page).all()
        
        return ResponseWrapper(
            success=True,
            message="Expenses retrieved successfully",
            data=PaginatedResponse(
                items=[ExpenseSchema.from_orm(expense) for expense in expenses],
                total=total,
                page=page,
                per_page=per_page,
                pages=(total + per_page - 1) // per_page
            )
        )
    except Exception as e:
        logger.error(f"Expenses retrieval error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve expenses"
        )

@router.get("/{expense_id}", response_model=ResponseWrapper)
async def get_expense(
    expense_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Get specific expense by ID"""
    try:
        expense = db.query(Expense).filter(
            Expense.id == expense_id,
            Expense.user_id == current_user.id
        ).first()
        
        if not expense:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Expense not found"
            )
        
        return ResponseWrapper(
            success=True,
            message="Expense retrieved successfully",
            data=ExpenseSchema.from_orm(expense)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Expense retrieval error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve expense"
        )

@router.put("/{expense_id}", response_model=ResponseWrapper)
async def update_expense(
    expense_id: int,
    expense_update: ExpenseUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Update expense"""
    try:
        expense = db.query(Expense).filter(
            Expense.id == expense_id,
            Expense.user_id == current_user.id
        ).first()
        
        if not expense:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Expense not found"
            )
        
        update_data = expense_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(expense, field, value)
        
        db.commit()
        db.refresh(expense)
        
        return ResponseWrapper(
            success=True,
            message="Expense updated successfully",
            data=ExpenseSchema.from_orm(expense)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Expense update error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Expense update failed"
        )

@router.delete("/{expense_id}", response_model=ResponseWrapper)
async def delete_expense(
    expense_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Delete expense"""
    try:
        expense = db.query(Expense).filter(
            Expense.id == expense_id,
            Expense.user_id == current_user.id
        ).first()
        
        if not expense:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Expense not found"
            )
        
        db.delete(expense)
        db.commit()
        
        return ResponseWrapper(
            success=True,
            message="Expense deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Expense deletion error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Expense deletion failed"
        )