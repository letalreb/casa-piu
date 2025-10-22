"""
Pydantic schemas for request/response models
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List
from datetime import datetime
from decimal import Decimal

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserCreate(UserBase):
    supabase_id: str

class UserUpdate(BaseModel):
    name: Optional[str] = None

class User(UserBase):
    id: int
    supabase_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Asset schemas
class AssetBase(BaseModel):
    type: str  # 'property' or 'vehicle'
    name: str
    details_json: Optional[Dict[str, Any]] = None

class AssetCreate(AssetBase):
    pass

class AssetUpdate(BaseModel):
    name: Optional[str] = None
    details_json: Optional[Dict[str, Any]] = None

class Asset(AssetBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Property specific schema
class PropertyDetails(BaseModel):
    address: str
    comune: str
    categoria_catastale: str
    rendita: Optional[Decimal] = None
    note: Optional[str] = None

# Vehicle specific schema
class VehicleDetails(BaseModel):
    targa: str
    marca: str
    modello: str
    anno: int
    tipo: str  # 'auto', 'moto', 'altro'

# Expense schemas
class ExpenseBase(BaseModel):
    asset_id: Optional[int] = None
    category: str
    amount: Decimal
    due_date: Optional[datetime] = None
    status: str = "pending"
    description: Optional[str] = None

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseUpdate(BaseModel):
    category: Optional[str] = None
    amount: Optional[Decimal] = None
    due_date: Optional[datetime] = None
    status: Optional[str] = None
    description: Optional[str] = None

class Expense(ExpenseBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Reminder schemas
class ReminderBase(BaseModel):
    asset_id: int
    type: str
    date: datetime
    message: str

class ReminderCreate(ReminderBase):
    pass

class Reminder(ReminderBase):
    id: int
    notified: bool = False
    created_at: datetime
    
    class Config:
        from_attributes = True

# Automation schemas
class AutomationBase(BaseModel):
    asset_id: int
    imu_calc: bool = False
    f24_gen: bool = False
    ocr: bool = False
    ai_suggestions: bool = False

class AutomationCreate(AutomationBase):
    pass

class AutomationUpdate(BaseModel):
    imu_calc: Optional[bool] = None
    f24_gen: Optional[bool] = None
    ocr: Optional[bool] = None
    ai_suggestions: Optional[bool] = None

class Automation(AutomationBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Document schemas
class DocumentBase(BaseModel):
    asset_id: int
    file_url: str
    file_type: str
    parsed_data_json: Optional[Dict[str, Any]] = None

class DocumentCreate(DocumentBase):
    pass

class Document(DocumentBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# IMU calculation schemas
class IMUCalculationRequest(BaseModel):
    rendita: Decimal
    categoria: str
    comune: str

class IMUCalculationResponse(BaseModel):
    importo_primo_acconto: Decimal
    importo_secondo_acconto: Decimal
    totale_annuo: Decimal
    scadenza_primo: str
    scadenza_secondo: str

# AI Suggestion schemas
class AISuggestionRequest(BaseModel):
    asset_id: Optional[int] = None
    period_months: int = 6

class AISuggestionResponse(BaseModel):
    suggestions: List[str]
    potential_savings: Optional[Decimal] = None
    analysis: str

# Response wrappers
class ResponseWrapper(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    per_page: int
    pages: int