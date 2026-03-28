# app/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv
# Cargar variables de entorno desde el archivo .env
load_dotenv()
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# Configuración de la cadena de conexión a PostgreSQL (Docker)
# SQLALCHEMY_DATABASE_URL = "postgresql://admin:password123@localhost:5432/especially_v1"

# Motor de conexión de SQLAlchemy
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Generador de sesiones para interactuar con la base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Clase base para la creación de modelos ORM
# Asegúrate de que el nombre sea 'Base' exactamente
Base = declarative_base()

# Dependencia para inyectar la sesión de DB en las rutas
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
