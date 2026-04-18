"""Punto de entrada de la aplicación FastAPI."""
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from .database import get_db
from .routers import auth, designs, images, orders, products, stores

app = FastAPI(
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

@app.get("/", tags=["General"])
def read_root():
    return {"message": "Bienvenido a la API de Especially 🌿"}


@app.get("/healthcheck", tags=["General"])
def health_check(db: Session = Depends(get_db)):
    """Devuelve el estado de salud de la API y de la base de datos."""
    try:
        db.execute(text("SELECT 1"))
        return {"status": "online", "database": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error de conexión a DB: {str(e)}",
        )
