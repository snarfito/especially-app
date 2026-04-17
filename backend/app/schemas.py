from pydantic import BaseModel, ConfigDict
from uuid import UUID
from decimal import Decimal
from typing import Optional, List
from datetime import datetime
from .models import OrderStatus

class StoreProfileBase(BaseModel):
    brand_name: str
    bio: Optional[str] = None
    is_business: bool = False

class StoreProfile(StoreProfileBase):
    store_id: UUID
    model_config = ConfigDict(from_attributes=True)

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: str
    base_price: Decimal
    is_customizable: bool = False
    stock_quantity: int = 0

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    product_id: UUID
    model_config = ConfigDict(from_attributes=True)

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    base_price: Optional[Decimal] = None
    is_customizable: Optional[bool] = None
    stock_quantity: Optional[int] = None

class UserBase(BaseModel):
    full_name: str
    email: str
    user_role: str
    city: Optional[str] = None

class User(UserBase):
    user_id: UUID
    store: Optional[StoreProfile] = None

    model_config = ConfigDict(from_attributes=True)
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserCreate(BaseModel):
    full_name: str
    email: str
    password: str
    user_role: str = "buyer"
    city: Optional[str] = None

class OrderBase(BaseModel):
    product_id: UUID
    quantity: int = 1
    custom_text: Optional[str] = None 
    custom_image_url: Optional[str] = None 

class OrderCreate(OrderBase):
    pass

class OrderResponse(OrderBase):
    order_id: UUID
    buyer_id: UUID
    total_price: float
    status: OrderStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Comentario agregado al final del archivo.
