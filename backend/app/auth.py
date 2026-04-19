"""
Especially API — Módulo de autenticación y seguridad.

Responsabilidades:
  - Hashing y verificación de contraseñas con bcrypt (passlib).
  - Generación y firma de JSON Web Tokens (JWT) con python-jose.
  - Lectura de credenciales sensibles desde variables de entorno.

Desarrollador: Fredy Hortua <fredy.hortua@gmail.com>
Proyecto:      Especially — Marketplace colombiano de personalización y artesanías
"""
import os
from datetime import datetime, timedelta
from typing import Optional

from dotenv import load_dotenv
from jose import jwt
from passlib.context import CryptContext

load_dotenv()

# Contexto de hashing; solo bcrypt en uso activo.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY: str = os.getenv("SECRET_KEY", "")
ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))


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
            token expira en 15 minutos.

    Returns:
        Token JWT codificado como cadena de texto.
    """
    to_encode = data.copy()
    expire = (
        datetime.utcnow() + expires_delta
        if expires_delta
        else datetime.utcnow() + timedelta(minutes=15)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
