"""
Database models for Casa&Più application
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, DECIMAL, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class User(Base):
    """User model for authentication and profile"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    supabase_id = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    assets = relationship("Asset", back_populates="owner")
    expenses = relationship("Expense", back_populates="user")

class Asset(Base):
    """Asset model for properties and vehicles"""
    __tablename__ = "assets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(String, nullable=False)  # 'property' or 'vehicle'
    name = Column(String, nullable=False)
    details_json = Column(JSON)  # Store specific details based on type
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="assets")
    expenses = relationship("Expense", back_populates="asset")
    reminders = relationship("Reminder", back_populates="asset")
    automations = relationship("Automation", back_populates="asset")
    documents = relationship("Document", back_populates="asset")

class Expense(Base):
    """Expense model for tracking costs"""
    __tablename__ = "expenses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=True)
    category = Column(String, nullable=False)  # 'imu', 'bollo', 'assicurazione', 'bolletta', etc.
    amount = Column(DECIMAL(10, 2), nullable=False)
    due_date = Column(DateTime, nullable=True)
    status = Column(String, default="pending")  # 'pending', 'paid', 'overdue'
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="expenses")
    asset = relationship("Asset", back_populates="expenses")

class Reminder(Base):
    """Reminder model for notifications"""
    __tablename__ = "reminders"
    
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    type = Column(String, nullable=False)  # 'imu', 'bollo', 'assicurazione', 'revisione'
    date = Column(DateTime, nullable=False)
    message = Column(Text, nullable=False)
    notified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    asset = relationship("Asset", back_populates="reminders")

class Automation(Base):
    """Automation settings for assets"""
    __tablename__ = "automations"
    
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    imu_calc = Column(Boolean, default=False)
    f24_gen = Column(Boolean, default=False)
    ocr = Column(Boolean, default=False)
    ai_suggestions = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    asset = relationship("Asset", back_populates="automations")

class Document(Base):
    """Document model for uploaded files"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    file_url = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # 'pdf', 'jpg', 'png'
    parsed_data_json = Column(JSON)  # OCR extracted data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    asset = relationship("Asset", back_populates="documents")