"""
Especially API — Punto de entrada de la aplicación FastAPI.

Responsabilidades:
  - Instancia y configura la aplicación FastAPI.
  - Registra el middleware CORS para el cliente web/móvil.
  - Monta todos los routers del dominio (auth, stores, products, images, orders, designs, payments).
  - Expone los endpoints raíz ('/') y de salud ('/healthcheck').

Desarrollador: Fredy Hortua <fredy.hortua@gmail.com>
Proyecto:      Especially — Marketplace colombiano de personalización y artesanías
"""
# app/main.py
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import crud
from .database import get_db
from .routers import auth, designs, images, orders, payments, products, stores

app: FastAPI = FastAPI(
    title="Especially API",
    description="Plataforma de personalización y marketplace de artesanías colombianas 🌿",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(stores.router)
app.include_router(products.router)
app.include_router(images.router)
app.include_router(orders.router)
app.include_router(designs.router)
app.include_router(payments.router)

@app.get("/", tags=["General"])
def read_root():
    """Devuelve el mensaje de bienvenida de la API."""
    return {"message": "Bienvenido a la API de Especially 🌿"}


@app.get("/healthcheck", tags=["General"])
def health_check(db: Session = Depends(get_db)):
    """Devuelve el estado de salud de la API y de la base de datos."""
    try:
        crud.ping_database(db)
        return {"status": "online", "database": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error de conexión a DB: {str(e)}",
        )
