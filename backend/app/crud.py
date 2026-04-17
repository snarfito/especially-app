# app/crud.py
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from . import models, schemas
from .auth import get_password_hash


# ─── USUARIOS ─────────────────────────────────────────────────────────────────

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_id(db: Session, user_id: UUID) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.user_id == user_id).first()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    db_user = models.User(
        full_name=user.full_name,
        email=user.email,
        password_hash=get_password_hash(user.password),
        user_role=user.user_role,
        city=user.city,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# ─── TIENDAS ──────────────────────────────────────────────────────────────────

def create_store(
    db: Session,
    store_data: schemas.StoreProfileBase,
    user_id: UUID,
) -> models.StoreProfile:
    db_store = models.StoreProfile(
        **store_data.model_dump(),
        user_id=user_id,
    )
    db.add(db_store)
    db.commit()
    db.refresh(db_store)
    return db_store


def get_store_by_user(db: Session, user_id: UUID) -> Optional[models.StoreProfile]:
    return db.query(models.StoreProfile).filter(
        models.StoreProfile.user_id == user_id
    ).first()


# ─── PRODUCTOS ────────────────────────────────────────────────────────────────

def get_products(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    category: Optional[str] = None,
) -> List[models.Product]:
    query = db.query(models.Product)
    if category:
        query = query.filter(models.Product.category == category)
    return query.offset(skip).limit(limit).all()


def get_product_by_id(db: Session, product_id: UUID) -> Optional[models.Product]:
    return db.query(models.Product).filter(
        models.Product.product_id == product_id
    ).first()


def create_product(
    db: Session,
    product: schemas.ProductCreate,
    store_id: UUID,
) -> models.Product:
    db_product = models.Product(
        **product.model_dump(),
        store_id=store_id,
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def update_product(
    db: Session,
    product: models.Product,
    product_data: schemas.ProductUpdate,
) -> models.Product:
    for key, value in product_data.model_dump(exclude_unset=True).items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product: models.Product) -> None:
    db.delete(product)
    db.commit()


# ─── PEDIDOS ──────────────────────────────────────────────────────────────────

def create_order(
    db: Session,
    order_data: schemas.OrderCreate,
    buyer_id: UUID,
) -> models.Order:
    """
    Crea una orden con sus items. Calcula el total sumando
    base_price * quantity de cada producto en la DB (nunca confía en el cliente).
    """
    total = Decimal("0")
    items_to_create = []

    for item_data in order_data.items:
        product = get_product_by_id(db, item_data.product_id)
        if not product:
            raise ValueError(f"Producto {item_data.product_id} no encontrado")

        unit_price = product.base_price
        total += unit_price * item_data.quantity

        items_to_create.append(models.OrderItem(
            product_id=item_data.product_id,
            design_id=item_data.design_id,
            quantity=item_data.quantity,
            unit_price=unit_price,
            size=item_data.size,
            garment_color=item_data.garment_color,
        ))

    db_order = models.Order(
        buyer_id=buyer_id,
        seller_id=None,
        status=models.OrderStatus.PENDING,
        shipping_type=order_data.shipping_type,
        total_amount=total,
        shipping_address=order_data.shipping_address,
    )
    db.add(db_order)
    db.flush()  # genera order_id sin commit para asociar los items

    for item in items_to_create:
        item.order_id = db_order.order_id
        db.add(item)

    db.commit()
    db.expire(db_order)  # fuerza releer created_at generado por el servidor
    db.refresh(db_order)
    return db_order


def get_orders_by_buyer(
    db: Session,
    buyer_id: UUID,
) -> List[models.Order]:
    return (
        db.query(models.Order)
        .filter(models.Order.buyer_id == buyer_id)
        .order_by(models.Order.created_at.desc())
        .all()
    )


def get_order_by_id(db: Session, order_id: UUID) -> Optional[models.Order]:
    return db.query(models.Order).filter(
        models.Order.order_id == order_id
    ).first()


def get_pending_orders(db: Session) -> List[models.Order]:
    """Devuelve pedidos pendientes sin un socio asignado."""
    return (
        db.query(models.Order)
        .filter(models.Order.status == models.OrderStatus.PENDING)
        .filter(models.Order.seller_id.is_(None))
        .order_by(models.Order.created_at.desc())
        .all()
    )


def assign_order_to_seller(
    db: Session,
    order: models.Order,
    seller_id: UUID,
) -> models.Order:
    order.seller_id = seller_id
    order.status = models.OrderStatus.ACCEPTED
    db.commit()
    db.refresh(order)
    return order


def update_order_status(
    db: Session,
    order: models.Order,
    new_status: models.OrderStatus,
) -> models.Order:
    order.status = new_status
    db.commit()
    db.refresh(order)
    return order


# ─── DISEÑOS PERSONALIZADOS ───────────────────────────────────────────────────

def create_custom_design(
    db: Session,
    design_data: schemas.CustomDesignCreate,
    user_id: UUID,
) -> models.CustomDesign:
    db_design = models.CustomDesign(
        user_id=user_id,
        canvas_json=design_data.canvas_json,
        preview_image_url=design_data.preview_image_url,
    )
    db.add(db_design)
    db.commit()
    db.refresh(db_design)
    return db_design


def get_designs_by_user(
    db: Session,
    user_id: UUID,
) -> List[models.CustomDesign]:
    return (
        db.query(models.CustomDesign)
        .filter(models.CustomDesign.user_id == user_id)
        .order_by(models.CustomDesign.created_at.desc())
        .all()
    )
