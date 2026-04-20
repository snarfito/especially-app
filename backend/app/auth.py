"""
Especially API — Módulo de autenticación y seguridad.

Responsabilidades:
  - Hashing y verificación de contraseñas con bcrypt (passlib).
  - Generación y firma de JSON Web Tokens (JWT) con python-jose.
  - Lectura de credenciales sensibles desde la configuración validada
    (``app.config.settings``).

Desarrollador: Fredy Hortua <fredy.hortua@gmail.com>
Proyecto:      Especially — Marketplace colombiano de personalización y artesanías
"""
# app/auth.py
from datetime import datetime, timedelta
from typing import Optional

from jose import jwt
from passlib.context import CryptContext

from .config import settings

# Contexto de hashing; solo bcrypt en uso activo.
pwd_context: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Re-export de los valores ya validados, para retrocompatibilidad con
# módulos que importan ``auth.SECRET_KEY`` / ``auth.ALGORITHM``.
SECRET_KEY: str = settings.SECRET_KEY
ALGORITHM: str = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES: int = settings.ACCESS_TOKEN_EXPIRE_MINUTES


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña en texto plano contra su hash bcrypt almacenado.

    Args:
        plain_password: Contraseña recibida del cliente.
        hashed_password: Hash guardado en base de datos.

    Returns:
        True si la contraseña es correcta, False en caso contrario.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Genera el hash bcrypt de una contraseña en texto plano.

    Args:
        password: Contraseña en texto plano a hashear.

    Returns:
        Hash bcrypt listo para persistir en base de datos.
    """
    return pwd_context.hash(password)


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Genera un JWT firmado con HS256.

    Args:
        data: Payload a codificar (debe incluir al menos la clave ``sub``).
        expires_delta: Duración de validez del token. Si no se provee, el
            token expira según ``ACCESS_TOKEN_EXPIRE_MINUTES`` (config).

    Returns:
        Token JWT codificado como cadena de texto.
    """
    to_encode = data.copy()
    expire = (
        datetime.utcnow() + expires_delta
        if expires_delta
        else datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
