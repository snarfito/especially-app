"""
Especially API — Router de diseños personalizados.

Endpoints:
  POST   /designs              → Guarda el canvas de Fabric.js del usuario.
  GET    /designs/my-designs   → Lista los diseños del usuario autenticado.
  GET    /designs/{id}         → Obtiene un diseño (solo el propietario).
  DELETE /designs/{id}         → Elimina un diseño (solo el propietario).

Desarrollador: Fredy Hortua <fredy.hortua@gmail.com>
Proyecto:      Especially — Marketplace colombiano de personalización y artesanías
"""
# app/routers/designs.py
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import crud, schemas
from ..database import get_db
from ..dependencies import get_current_user
from ..models import User

router: APIRouter = APIRouter(prefix="/designs", tags=["Diseños"])


@router.post("", response_model=schemas.CustomDesign, status_code=201)
def save_design(
    design_data: schemas.CustomDesignCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Guarda el estado del canvas de Fabric.js para el usuario autenticado.
    El campo canvas_json contiene las capas, posiciones y filtros del editor.
    El campo preview_image_url es la miniatura generada por el frontend (base64 o URL de R2).
    """
    return crud.create_custom_design(db, design_data, current_user.user_id)


@router.get("/my-designs", response_model=List[schemas.CustomDesign])
def get_my_designs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Devuelve todos los diseños guardados por el usuario autenticado."""
    return crud.get_designs_by_user(db, current_user.user_id)


@router.get("/{design_id}", response_model=schemas.CustomDesign)
def get_design(
    design_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Devuelve un diseño por ID.
    Solo el propietario puede acceder a sus propios diseños.
    """
    design = crud.get_design_by_id(db, design_id)
    if not design:
        raise HTTPException(status_code=404, detail="Diseño no encontrado")
    if design.user_id != current_user.user_id:
        raise HTTPException(
            status_code=403,
            detail="No tienes permiso para acceder a este diseño",
        )
    return design


@router.delete("/{design_id}", status_code=204)
def delete_design(
    design_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Elimina un diseño guardado. Solo el propietario puede eliminarlo."""
    design = crud.get_design_by_id(db, design_id)
    if not design:
        raise HTTPException(status_code=404, detail="Diseño no encontrado")
    if design.user_id != current_user.user_id:
        raise HTTPException(
            status_code=403,
            detail="No tienes permiso para eliminar este diseño",
        )
    crud.delete_custom_design(db, design)
