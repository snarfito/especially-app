# app/schemas.py
from pydantic import BaseModel, ConfigDict
from uuid import UUID
from decimal import Decimal
from typing import Optional, List
from datetime import datetime
from .models import OrderStatus

# --- ESQUEMAS DE TIENDA (STORE) ---

# Define cómo se muestra la marca (ej: SoulsColors) al público
class StoreProfileBase(BaseModel):
    brand_name: str
    bio: Optional[str] = None
    is_business: bool = False

# Esquema completo que incluye el ID generado por la base de datos
class StoreProfile(StoreProfileBase):
    store_id: UUID

    # Permite la compatibilidad con modelos de SQLAlchemy 2.0
    model_config = ConfigDict(from_attributes=True)


# --- ESQUEMAS DE PRODUCTO (PRODUCT) ---

# Atributos básicos que comparten todas las versiones del producto
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: str
    base_price: Decimal
    is_customizable: bool = False
    stock_quantity: int = 0

# Esquema para la creación de nuevos productos (Entrada)
class ProductCreate(ProductBase):
    pass

# Esquema para la lectura de productos (Salida)
# Aquí es donde la API devuelve la información completa al Frontend
class Product(ProductBase):
    product_id: UUID
    
    # Próximamente vincularemos el objeto StoreProfile aquí 
    # para mostrar la marca SoulsColors o Fabio Hortua
    
    model_config = ConfigDict(from_attributes=True)

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    base_price: Optional[Decimal] = None
    is_customizable: Optional[bool] = None
    stock_quantity: Optional[int] = None


# --- ESQUEMAS DE USUARIO (USER) ---

# Datos mínimos para mostrar un perfil de usuario o artista
class UserBase(BaseModel):
    full_name: str
    email: str
    user_role: str
    city: Optional[str] = None

class User(UserBase):
    user_id: UUID
    # Incluye el perfil de marca si el usuario es un Socio Productor
    store: Optional[StoreProfile] = None

    model_config = ConfigDict(from_attributes=True)

# Esquema para la respuesta del Login
class Token(BaseModel):
    access_token: str
    token_type: str

# Datos que viajan dentro del token (Payload)
class TokenData(BaseModel):
    email: Optional[str] = None


# Datos necesarios para crear un nuevo usuario
class UserCreate(BaseModel):
    full_name: str
    email: str
    password: str # Contraseña en texto plano que recibimos
    user_role: str = "buyer"
    city: Optional[str] = None

# === ESQUEMAS PARA PEDIDOS (ORDERS) ===

class OrderBase(BaseModel):
    product_id: UUID
    quantity: int = 1
    # Campos de personalización para los artistas y socios
    custom_text: Optional[str] = None 
    custom_image_url: Optional[str] = None 

class OrderCreate(OrderBase):
    pass
    # No pedimos el total_price ni el buyer_id aquí. 
    # El backend los calculará por seguridad para que el cliente no haga trampa.

class OrderResponse(OrderBase):
    order_id: UUID
    buyer_id: UUID
    total_price: float
    status: OrderStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)