# app/routers/images.py
"""
Endpoints para subir y gestionar imágenes de productos.
Las imágenes se almacenan en Cloudflare R2 y sus URLs en product_images.
"""
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, Form
from sqlalchemy.orm import Session
from typing import List

from .. import crud, schemas
from ..database import get_db
from ..dependencies import get_owned_product, require_store_owner
from ..models import Product, StoreProfile
from .. import storage

router = APIRouter(prefix="/products", tags=["Imágenes de productos"])

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


@router.post("/{product_id}/images", response_model=schemas.ProductImage, status_code=201)
async def upload_product_image(
    product_id: UUID,
    file: UploadFile = File(...),
    view_type: str = Form(default="main"),
    display_order: int = Form(default=0),
    db: Session = Depends(get_db),
    product: Product = Depends(get_owned_product),
):
    """
    Sube una imagen para un producto. Solo el dueño de la tienda puede hacerlo.
    
    view_type: 'main' | 'front' | 'back' | 'sleeve_right' | 'sleeve_left'
    display_order: orden de aparición (0 = principal)
    """
    # Validar tipo de archivo
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de archivo no permitido. Usa: {', '.join(ALLOWED_CONTENT_TYPES)}",
        )

    # Leer y validar tamaño
    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="El archivo supera el límite de 5 MB",
        )

    # Subir a R2 — devuelve URL pública directa
    url = storage.upload_file(
        file_bytes=file_bytes,
        content_type=file.content_type,
        folder=f"products/{product_id}",
    )

    # Guardar en DB
    image_data = schemas.ProductImageCreate(
        url=url,
        view_type=view_type,
        display_order=display_order,
    )
    return crud.create_product_image(db, image_data, product.product_id)


@router.get("/{product_id}/images", response_model=List[schemas.ProductImage])
def list_product_images(
    product_id: UUID,
    db: Session = Depends(get_db),
):
    """Devuelve todas las imágenes de un producto ordenadas por display_order."""
    return crud.get_product_images(db, product_id)


@router.delete("/{product_id}/images/{image_id}", status_code=204)
def delete_product_image(
    image_id: UUID,
    db: Session = Depends(get_db),
    product: Product = Depends(get_owned_product),
):
    """Elimina una imagen del producto y del bucket R2."""
    image = crud.get_product_image_by_id(db, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Imagen no encontrada")
    if image.product_id != product.product_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar esta imagen")

    # Eliminar de R2 (extraemos la key de la URL)
    # La URL es del tipo: https://endpoint/bucket/products/uuid/filename.jpg
    try:
        key = "/".join(image.url.split("/")[-3:])  # products/uuid/filename.jpg
        storage.delete_file(key)
    except Exception:
        pass  # Si falla R2 igual borramos el registro

    crud.delete_product_image(db, image)
