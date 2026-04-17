# app/models.py
import enum
import uuid
from sqlalchemy import (
    Column, String, Boolean, ForeignKey, Integer,
    Numeric, DateTime, Text, Enum
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


# ─── ENUMS ────────────────────────────────────────────────────────────────────

class OrderStatus(str, enum.Enum):
    PENDING   = "pendiente"
    ACCEPTED  = "aceptado"
    PRODUCING = "produciendo"
    SHIPPED   = "enviado"
    DELIVERED = "entregado"
    CANCELLED = "cancelado"

class ShippingType(str, enum.Enum):
    NORMAL = "normal"
    URGENT = "urgente"


# ─── USUARIOS ─────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    user_id       = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name     = Column(String(100), nullable=False)
    email         = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    user_role     = Column(String(20), default="buyer")  # buyer | seller | designer
    city          = Column(String(50))
    created_at    = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    store            = relationship("StoreProfile", uselist=False, back_populates="owner")
    orders_as_buyer  = relationship("Order", foreign_keys="Order.buyer_id", back_populates="buyer")
    custom_designs   = relationship("CustomDesign", back_populates="user")


# ─── PERFIL DE TIENDA ─────────────────────────────────────────────────────────

class StoreProfile(Base):
    __tablename__ = "store_profiles"

    store_id    = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id     = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), unique=True)
    brand_name  = Column(String(150), nullable=False)
    bio         = Column(Text)
    logo_url    = Column(String)
    is_business = Column(Boolean, default=False)

    # Relaciones
    owner    = relationship("User", back_populates="store")
    products = relationship("Product", back_populates="store")


# ─── PRODUCTOS ────────────────────────────────────────────────────────────────

class Product(Base):
    __tablename__ = "products"

    product_id      = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    store_id        = Column(UUID(as_uuid=True), ForeignKey("store_profiles.store_id"), nullable=True)
    name            = Column(String(150), nullable=False)
    description     = Column(Text)
    category        = Column(String(50))
    base_price      = Column(Numeric(12, 2), nullable=False)
    is_customizable = Column(Boolean, default=False)
    stock_quantity  = Column(Integer, default=0)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    store       = relationship("StoreProfile", back_populates="products")
    images      = relationship("ProductImage", back_populates="product",
                               cascade="all, delete-orphan")
    order_items = relationship("OrderItem", back_populates="product")


class ProductImage(Base):
    """Fotos del producto por vista: frente, espalda, manga, etc."""
    __tablename__ = "product_images"

    image_id      = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id    = Column(UUID(as_uuid=True), ForeignKey("products.product_id",
                            ondelete="CASCADE"), nullable=False)
    url           = Column(String, nullable=False)
    # Valores: 'front' | 'back' | 'sleeve_right' | 'sleeve_left' | 'main'
    view_type     = Column(String(30), default="main")
    display_order = Column(Integer, default=0)

    # Relaciones
    product = relationship("Product", back_populates="images")


# ─── DISEÑOS PERSONALIZADOS ───────────────────────────────────────────────────

class CustomDesign(Base):
    """Estado del canvas de Fabric.js guardado por el comprador."""
    __tablename__ = "custom_designs"

    design_id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id           = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    canvas_json       = Column(JSONB, nullable=False)   # capas, posiciones, filtros
    preview_image_url = Column(Text)                    # miniatura para carrito (R2)
    created_at        = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    user        = relationship("User", back_populates="custom_designs")
    order_items = relationship("OrderItem", back_populates="design")


# ─── PEDIDOS ──────────────────────────────────────────────────────────────────

class Order(Base):
    __tablename__ = "orders"

    order_id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    buyer_id         = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    seller_id        = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=True)
    status           = Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    shipping_type    = Column(Enum(ShippingType), default=ShippingType.NORMAL)
    total_amount     = Column(Numeric(12, 2), nullable=False)
    shipping_address = Column(Text, nullable=False)
    created_at       = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    buyer  = relationship("User", foreign_keys=[buyer_id], back_populates="orders_as_buyer")
    seller = relationship("User", foreign_keys=[seller_id])
    items  = relationship("OrderItem", back_populates="order",
                          cascade="all, delete-orphan")


class OrderItem(Base):
    """Línea de detalle de un pedido: un producto + su diseño personalizado."""
    __tablename__ = "order_items"

    item_id       = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id      = Column(UUID(as_uuid=True), ForeignKey("orders.order_id",
                            ondelete="CASCADE"), nullable=False)
    product_id    = Column(UUID(as_uuid=True), ForeignKey("products.product_id"), nullable=False)
    design_id     = Column(UUID(as_uuid=True), ForeignKey("custom_designs.design_id"), nullable=True)
    quantity      = Column(Integer, nullable=False, default=1)
    unit_price    = Column(Numeric(12, 2), nullable=False)  # precio histórico al momento de comprar
    size          = Column(String(10))    # XS | S | M | L | XL | 2XL | 3XL
    garment_color = Column(String(30))   # color de la prenda (hex o nombre)

    # Relaciones
    order   = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
    design  = relationship("CustomDesign", back_populates="order_items")
