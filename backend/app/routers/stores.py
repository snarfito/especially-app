from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db
from ..dependencies import require_user_without_store
from ..models import User

router = APIRouter(prefix="/store", tags=["Socios"])

@router.post("", response_model=schemas.StoreProfile, status_code=201)
def create_store(
    store_data: schemas.StoreProfileBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user_without_store),
):
    """Crea un perfil comercial para el usuario autenticado."""
    return crud.create_store(db, store_data, current_user.user_id)
