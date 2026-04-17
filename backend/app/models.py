import enum
from sqlalchemy import Column, String, Boolean, ForeignKey, Integer, Numeric, DateTime, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

import uuid
from datetime import datetime

from .database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    user_role = Column(String(20), default="buyer")
    city = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    orders = relationship("Order", back_populates="buyer", foreign_keys="Order.buyer_id")
    store = relationship("StoreProfile", uselist=False, back_populates="owner")

class Product(Base):
    __tablename__ = "products"

    product_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    store_id = Column(UUID(as_uuid=True), ForeignKey("store_profiles.store_id"), nullable=True)
    
    name = Column(String(150), nullable=False)
    description = Column(Text)
    category = Column(String(50))
    base_price = Column(Numeric(12, 2), nullable=False)
    is_customizable = Column(Boolean, default=False)
    stock_quantity = Column(Integer, default=0)

    store = relationship("StoreProfile")

class OrderStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SHIPPED = "SHIPPED"
    COMPLETED = "COMPLETED"

class Order(Base):
    __tablename__ = "orders"

    order_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    buyer_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    seller_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.product_id"), nullable=False)
    
    quantity = Column(Numeric, default=1)
    total_price = Column(Numeric(12, 2))
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    
    custom_text = Column(Text, nullable=True) 
    custom_image_url = Column(String(500), nullable=True) 
    
    created_at = Column(DateTime, default=datetime.utcnow)

    buyer = relationship("User", back_populates="orders", foreign_keys=[buyer_id])
    seller = relationship("User", foreign_keys=[seller_id])
    product = relationship("Product")

class StoreProfile(Base):
    __tablename__ = "store_profiles"

    store_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), unique=True)
    brand_name = Column(String(150), nullable=False)
    bio = Column(Text)
    logo_url = Column(String)
    is_business = Column(Boolean, default=False)

    owner = relationship("User", back_populates="store")
