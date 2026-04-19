"""
Especially API — Router del marketplace de productos.

Endpoints:
  GET    /products            → Listado paginado (filtro opcional por categoría).
  GET    /products/{id}       → Detalle de un producto.
  POST   /products            → Crea producto (requiere tienda activa).
  PUT    /products/{id}       → Actualiza producto propio.
  DELETE /products/{id}       → Elimina producto propio.

Desarrollador: Fredy Hortua <fredy.hortua@gmail.com>
Proyecto:      Especially — Marketplace colombiano de personalización y artesanías
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db
from ..dependencies import get_owned_product, require_store_owner
from ..models import Product, StoreProfile

router = APIRouter(prefix="/products", tags=["Marketplace"])

@router.get("", response_model=List[schemas.Product])
def list_products(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, le=100),
    category: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    """Devuelve productos con paginación y filtro opcional por categoría."""
    return crud.get_products(db, skip=skip, limit=limit, category=category)


@router.get("/{product_id}", response_model=schemas.Product)
def get_product(product_id: UUID, db: Session = Depends(get_db)):
    """Devuelve un producto por identificador."""
    product = crud.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product


@router.post("", response_model=schemas.Product, status_code=201)
def create_product(
    product: schemas.ProductCreate,
    db: Session = Depends(get_db),
    current_store: StoreProfile = Depends(require_store_owner),
):
    """Crea un producto para la tienda autenticada."""
    return crud.create_product(db, product, current_store.store_id)


@router.put("/{product_id}", response_model=schemas.Product)
def update_product(
    product_data: schemas.ProductUpdate,
    product: Product = Depends(get_owned_product),
    db: Session = Depends(get_db),
):
    """Actualiza un producto existente."""
    return crud.update_product(db, product, product_data)


@router.delete("/{product_id}", status_code=204)
def delete_product(
    product: Product = Depends(get_owned_product),
    db: Session = Depends(get_db),
):
    """Elimina un producto existente."""
    crud.delete_product(db, product)
