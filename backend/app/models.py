# app/models.py
import enum
from sqlalchemy import Column, String, Boolean, ForeignKey, Integer, Numeric, DateTime, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

import uuid
from datetime import datetime

from .database import Base

# Definición del modelo de Usuario (Identidad personal y legal)
class User(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    user_role = Column(String(20), default="buyer")
    city = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones: Un usuario puede tener pedidos y un perfil de marca (Store)
    orders = relationship("Order", back_populates="buyer")
    store = relationship("StoreProfile", uselist=False, back_populates="owner")

# Definición del catálogo de productos (Camisetas, Biblias, Mandalas)
class Product(Base):
    __tablename__ = "products"

    product_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # NUEVA COLUMNA: Vinculación con la tienda
    store_id = Column(UUID(as_uuid=True), ForeignKey("store_profiles.store_id"), nullable=True)
    
    name = Column(String(150), nullable=False)
    description = Column(Text)
    category = Column(String(50))
    base_price = Column(Numeric(12, 2), nullable=False)
    is_customizable = Column(Boolean, default=False)
    stock_quantity = Column(Integer, default=0)

    # Relación para poder acceder a los datos de la marca desde el producto
    store = relationship("StoreProfile")

class OrderStatus(str, enum.Enum):
    PENDING = "pendiente"
    PROCESSING = "en proceso"
    SHIPPED = "enviado"
    COMPLETED = "completado"

# Gestión de pedidos y estados de entrega
class Order(Base):
    __tablename__ = "orders"

    order_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    buyer_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.product_id"), nullable=False)
    
    # Datos de la transacción
    quantity = Column(Numeric, default=1)
    total_price = Column(Numeric(12, 2))
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    
    # PERSONALIZACIÓN
    # Para Bibi/Fabio: "Nombre en dorado, cuero café"
    custom_text = Column(Text, nullable=True) 
    
    # Para las camisetas: URL de la imagen subida a un storage (S3/Google Cloud)
    custom_image_url = Column(String(500), nullable=True) 
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    buyer = relationship("User", back_populates="orders")
    product = relationship("Product")

# Perfil de marca: Permite nombres comerciales como 'SoulsColors' o 'Fabio Hortua'
class StoreProfile(Base):
    __tablename__ = "store_profiles"

    store_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), unique=True)
    brand_name = Column(String(150), nullable=False)
    bio = Column(Text)
    logo_url = Column(String)
    is_business = Column(Boolean, default=False)

    # Relación inversa hacia el usuario dueño de la marca
    owner = relationship("User", back_populates="store")
