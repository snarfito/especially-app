from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from . import auth, database, models, schemas

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(
    db: Session = Depends(database.get_db),
    token: str = Depends(oauth2_scheme),
):
    credentials_exception = HTTPException(
        status_code=401,
        detail="No se pudo validar el token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user


def require_store_owner(
    current_user: models.User = Depends(get_current_user),
) -> models.StoreProfile:
    if not current_user.store:
        raise HTTPException(
            status_code=403,
            detail="Necesitas un perfil de marca activo para realizar esta acción",
        )
    return current_user.store


def require_user_without_store(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if current_user.store:
        raise HTTPException(
            status_code=400,
            detail="El usuario ya tiene un perfil de marca",
        )
    return current_user


def get_product_or_404(
    product_id: UUID,
    db: Session = Depends(database.get_db),
) -> models.Product:
    product = db.query(models.Product).filter(
        models.Product.product_id == product_id
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    return product


def get_order_product(
    order_data: schemas.OrderCreate,
    db: Session = Depends(database.get_db),
) -> models.Product:
    return get_product_or_404(order_data.product_id, db)


def get_owned_product(
    product_id: UUID,
    db: Session = Depends(database.get_db),
    current_store: models.StoreProfile = Depends(require_store_owner),
) -> models.Product:
    product = get_product_or_404(product_id, db)

    if product.store_id != current_store.store_id:
        raise HTTPException(
            status_code=403,
            detail="No tienes permiso para acceder a este producto",
        )

    return product
