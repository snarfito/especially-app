"""
Especially API — Router de autenticación y gestión de usuarios.

Endpoints:
  POST /token      → Genera un JWT (flujo OAuth2 password).
  POST /users      → Registro de nueva cuenta.
  GET  /users/me   → Perfil del usuario autenticado.

Desarrollador: Fredy Hortua <fredy.hortua@gmail.com>
Proyecto:      Especially — Marketplace colombiano de personalización y artesanías
"""
# app/routers/auth.py
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import auth, crud, schemas
from ..database import get_db
from ..dependencies import get_current_user
from ..models import User

router: APIRouter = APIRouter(tags=["Seguridad y Usuarios"])

@router.post("/token", response_model=schemas.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Autentica un usuario con el flujo OAuth2 password."""
    user = crud.get_user_by_email(db, email=form_data.username)

    if not user or not auth.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = auth.create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/users", response_model=schemas.User, status_code=201)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Crea una cuenta de usuario."""
    existing = crud.get_user_by_email(db, email=user.email)
    if existing:
        raise HTTPException(
            status_code=400,
            detail="El correo ya está registrado",
        )
    return crud.create_user(db, user)


@router.get("/users/me", response_model=schemas.User)
def get_me(current_user: User = Depends(get_current_user)):
    """Devuelve el perfil del usuario autenticado."""
    return current_user
