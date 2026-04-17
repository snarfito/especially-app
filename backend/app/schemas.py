# app/schemas.py
from pydantic import BaseModel, ConfigDict
from uuid import UUID
from decimal import Decimal
from typing import Optional, List
from datetime import datetime
from .models import OrderStatus, ShippingType


# ─── TIENDA ───────────────────────────────────────────────────────────────────

class StoreProfileBase(BaseModel):
    brand_name: str
    bio: Optional[str] = None
    is_business: bool = False

class StoreProfileCreate(StoreProfileBase):
    pass

class StoreProfile(StoreProfileBase):
    store_id: UUID
    logo_url: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


# ─── IMÁGENES DE PRODUCTO ─────────────────────────────────────────────────────

class ProductImageCreate(BaseModel):
    url: str
    view_type: str = "main"
    display_order: int = 0

class ProductImage(ProductImageCreate):
    image_id: UUID
    model_config = ConfigDict(from_attributes=True)


# ─── PRODUCTOS ────────────────────────────────────────────────────────────────

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: str
    base_price: Decimal
    is_customizable: bool = False
    stock_quantity: int = 0

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    base_price: Optional[Decimal] = None
    is_customizable: Optional[bool] = None
    stock_quantity: Optional[int] = None

class Product(ProductBase):
    product_id: UUID
    store: Optional[StoreProfile] = None
    images: List[ProductImage] = []
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


# ─── USUARIOS ─────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    full_name: str
    email: str
    password: str
    user_role: str = "buyer"
    city: Optional[str] = None

class User(BaseModel):
    user_id: UUID
    full_name: str
    email: str
    user_role: str
    city: Optional[str] = None
    store: Optional[StoreProfile] = None
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None


# ─── DISEÑOS PERSONALIZADOS ───────────────────────────────────────────────────

class CustomDesignCreate(BaseModel):
    canvas_json: dict
    preview_image_url: Optional[str] = None

class CustomDesign(CustomDesignCreate):
    design_id: UUID
    user_id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ─── PEDIDOS ──────────────────────────────────────────────────────────────────

class OrderItemCreate(BaseModel):
    product_id: UUID
    design_id: Optional[UUID] = None
    quantity: int = 1
    size: Optional[str] = None
    garment_color: Optional[str] = None

class OrderItem(OrderItemCreate):
    item_id: UUID
    unit_price: Decimal
    model_config = ConfigDict(from_attributes=True)

class OrderCreate(BaseModel):
    shipping_type: ShippingType = ShippingType.NORMAL
    shipping_address: str
    items: List[OrderItemCreate]

class Order(BaseModel):
    order_id: UUID
    status: OrderStatus
    shipping_type: Optional[ShippingType] = None
    total_amount: Decimal
    shipping_address: str
    created_at: Optional[datetime] = None
    items: List[OrderItem] = []
    model_config = ConfigDict(from_attributes=True)

class OrderStatusUpdate(BaseModel):
    status: OrderStatus
