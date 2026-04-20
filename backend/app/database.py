"""
Especially API — Configuración de la base de datos.

Responsabilidades:
  - Crea el engine de SQLAlchemy apuntando a la URL de PostgreSQL definida
    en la configuración validada (``app.config.settings``).
  - Expone ``SessionLocal`` para la inyección de dependencias en FastAPI.
  - Define ``Base`` (DeclarativeBase) que importan todos los modelos ORM.
  - Provee ``get_db``, generador de sesión con cierre garantizado.

Desarrollador: Fredy Hortua <fredy.hortua@gmail.com>
Proyecto:      Especially — Marketplace colombiano de personalización y artesanías
"""
# app/database.py
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from .config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Generador de sesión SQLAlchemy para inyección de dependencias.

    Abre una sesión al inicio del request y garantiza su cierre al finalizar,
    independientemente de si ocurrió un error.

    Yields:
        Session: Sesión activa de SQLAlchemy.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
