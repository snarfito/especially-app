"""
Especially API — Dependencias reutilizables de FastAPI.

Provee funciones de dependencia (``Depends``) que encapsulan:
  - Autenticación: extracción y validación del JWT Bearer.
  - Autorización: verificación de roles y propiedad de recursos.
  - Atajos 404: resolución de entidades o excepción inmediata.

Desarrollador: Fredy Hortua <fredy.hortua@gmail.com>
Proyecto:      Especially — Marketplace colombiano de personalización y artesanías
"""
# app/dependencies.py
from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from . import auth, crud, database, models

oauth2_scheme: OAuth2PasswordBearer = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(
    db: Session = Depends(database.get_db),
    token: str = Depends(oauth2_scheme),
) -> models.User:
    """Extrae y valida el JWT Bearer; devuelve el usuario autenticado.

    Args:
        db: Sesión activa de SQLAlchemy.
        token: Token JWT extraído del header ``Authorization: Bearer``.

    Returns:
        Instancia de ``User`` correspondiente al token.

    Raises:
        HTTPException 401: Si el token es inválido, expirado o el usuario no existe.
    """
    credentials_exception = HTTPException(
        status_code=401,
        detail="No se pudo validar el token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        email: Optional[str] = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = crud.get_user_by_email(db, email)
    if user is None:
        raise credentials_exception
    return user


def require_store_owner(
    current_user: models.User = Depends(get_current_user),
) -> models.StoreProfile:
    """Verifica que el usuario autenticado tenga un perfil de tienda activo.

    Args:
        current_user: Usuario resuelto por ``get_current_user``.

    Returns:
        Instancia de ``StoreProfile`` del usuario.

    Raises:
        HTTPException 403: Si el usuario no tiene perfil de marca.
    """
    if not current_user.store:
        raise HTTPException(
            status_code=403,
            detail="Necesitas un perfil de marca activo para realizar esta acción",
        )
    return current_user.store


def require_user_without_store(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    """Verifica que el usuario autenticado aún no tenga perfil de tienda.

    Usado al crear un nuevo ``StoreProfile`` para evitar duplicados.

    Args:
        current_user: Usuario resuelto por ``get_current_user``.

    Returns:
        Instancia de ``User`` si no tiene tienda.

    Raises:
        HTTPException 400: Si el usuario ya posee un perfil de marca.
    """
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
    """Resuelve un producto por UUID o lanza 404.

    Args:
        product_id: UUID del producto a buscar.
        db: Sesión activa de SQLAlchemy.

    Returns:
        Instancia de ``Product`` si existe.

    Raises:
        HTTPException 404: Si el producto no existe en la base de datos.
    """
    product = crud.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product


def get_owned_product(
    product_id: UUID,
    db: Session = Depends(database.get_db),
    current_store: models.StoreProfile = Depends(require_store_owner),
) -> models.Product:
    """Resuelve un producto y verifica que pertenezca a la tienda autenticada.

    Args:
        product_id: UUID del producto a buscar.
        db: Sesión activa de SQLAlchemy.
        current_store: Tienda resuelta por ``require_store_owner``.

    Returns:
        Instancia de ``Product`` si existe y pertenece a la tienda.

    Raises:
        HTTPException 404: Si el producto no existe.
        HTTPException 403: Si el producto pertenece a otra tienda.
    """
    product = get_product_or_404(product_id, db)
    if product.store_id != current_store.store_id:
        raise HTTPException(
            status_code=403,
            detail="No tienes permiso para acceder a este producto",
        )
    return product


def get_order_or_404(
    order_id: UUID,
    db: Session = Depends(database.get_db),
) -> models.Order:
    """Resuelve una orden por UUID o lanza 404.

    Args:
        order_id: UUID de la orden a buscar.
        db: Sesión activa de SQLAlchemy.

    Returns:
        Instancia de ``Order`` si existe.

    Raises:
        HTTPException 404: Si la orden no existe en la base de datos.
    """
    order = crud.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return order


def get_assigned_order(
    order_id: UUID,
    order: models.Order = Depends(get_order_or_404),
    current_store: models.StoreProfile = Depends(require_store_owner),
) -> models.Order:
    """Verifica que el pedido esté asignado al socio productor autenticado.

    Args:
        order_id: UUID de la orden (usado por ``get_order_or_404``).
        order: Orden resuelta por ``get_order_or_404``.
        current_store: Tienda resuelta por ``require_store_owner``.

    Returns:
        Instancia de ``Order`` si el socio autenticado es el asignado.

    Raises:
        HTTPException 403: Si la orden pertenece a otro socio.
    """
    if order.seller_id != current_store.user_id:
        raise HTTPException(
            status_code=403,
            detail="No tienes permiso para gestionar este pedido",
        )
    return order
