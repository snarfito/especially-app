# app/routers/orders.py
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import crud, schemas
from ..database import get_db
from ..dependencies import (
    get_assigned_order,
    get_current_user,
    get_order_or_404,
    require_store_owner,
)
from ..models import Order, OrderStatus, StoreProfile, User

router = APIRouter(prefix="/orders", tags=["Pedidos"])


@router.post("", response_model=schemas.Order, status_code=201)
def create_order(
    order_data: schemas.OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Crea un pedido con uno o varios productos.
    El total se calcula en el backend — el cliente nunca envía precios.
    """
    try:
        return crud.create_order(db, order_data, current_user.user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/my-orders", response_model=List[schemas.Order])
def get_my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Devuelve los pedidos del comprador autenticado."""
    return crud.get_orders_by_buyer(db, current_user.user_id)


@router.get("/available", response_model=List[schemas.Order])
def get_available_orders(
    db: Session = Depends(get_db),
    _store: StoreProfile = Depends(require_store_owner),
):
    """Devuelve los pedidos pendientes disponibles para que un socio los tome."""
    return crud.get_pending_orders(db)


@router.post("/{order_id}/accept", response_model=schemas.Order)
def accept_order(
    db: Session = Depends(get_db),
    current_store: StoreProfile = Depends(require_store_owner),
    order: Order = Depends(get_order_or_404),
):
    """El socio autenticado acepta y toma un pedido pendiente."""
    if order.status != OrderStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail=f"El pedido no está disponible (estado actual: {order.status.value})",
        )
    if order.seller_id is not None:
        raise HTTPException(
            status_code=400,
            detail="El pedido ya fue tomado por otro socio",
        )
    return crud.assign_order_to_seller(db, order, current_store.user_id)


@router.put("/{order_id}/status", response_model=schemas.Order)
def update_order_status(
    status_update: schemas.OrderStatusUpdate,
    db: Session = Depends(get_db),
    order: Order = Depends(get_assigned_order),
):
    """El socio asignado actualiza el estado de su pedido."""
    return crud.update_order_status(db, order, status_update.status)
