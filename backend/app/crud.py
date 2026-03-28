# crud.py
from sqlalchemy.orm import Session
from . import models, schemas
from .auth import get_password_hash

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed = get_password_hash(user.password)
    db_user = models.User(
        full_name=user.full_name,
        email=user.email,
        password_hash=hashed,
        user_role=user.user_role,
        city=user.city
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_products(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Product).offset(skip).limit(limit).all()

def create_order(db: Session, order: schemas.OrderCreate, buyer_id, product):
    total = product.base_price * order.quantity
    db_order = models.Order(
        buyer_id=buyer_id,
        product_id=product.product_id,
        quantity=order.quantity,
        total_price=total,
        custom_text=order.custom_text,
        custom_image_url=order.custom_image_url
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order