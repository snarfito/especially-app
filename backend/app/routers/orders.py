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
    get_order_product,
    require_store_owner,
)
from ..models import Order, OrderStatus, Product, StoreProfile, User

router = APIRouter(prefix="/orders", tags=["Pedidos"])

@router.post("", response_model=schemas.OrderResponse, status_code=201)
def create_order(
    order_data: schemas.OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    product: Product = Depends(get_order_product),
):
    """Crea un pedido para el comprador autenticado."""
    return crud.create_order(db, order_data, current_user.user_id, product)


@router.get("/my-orders", response_model=List[schemas.OrderResponse])
def get_my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Devuelve los pedidos del comprador autenticado."""
    return crud.get_orders_by_buyer(db, current_user.user_id)

@router.get("/available", response_model=List[schemas.OrderResponse])
def get_available_orders(
    db: Session = Depends(get_db),
    _store: StoreProfile = Depends(require_store_owner),
):
    """Devuelve los pedidos pendientes disponibles para asignación."""
    return crud.get_pending_orders(db)


@router.post("/{order_id}/accept", response_model=schemas.OrderResponse)
def accept_order(
    db: Session = Depends(get_db),
    current_store: StoreProfile = Depends(require_store_owner),
    order: Order = Depends(get_order_or_404),
):
    """Asigna un pedido pendiente al socio autenticado."""
    if order.status != OrderStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail=f"El pedido ya fue procesado (estado actual: {order.status})",
        )

    if order.seller_id is not None:
        raise HTTPException(status_code=400, detail="El pedido ya fue tomado por otro socio")

    return crud.assign_order_to_seller(db, order, current_store.user_id)


@router.put("/{order_id}/status", response_model=schemas.OrderResponse)
def update_order_status(
    order_id: UUID,
    new_status: OrderStatus,
    db: Session = Depends(get_db),
    order: Order = Depends(get_assigned_order),
):
    """Actualiza el estado de un pedido asignado."""
    return crud.update_order_status(db, order, new_status)
