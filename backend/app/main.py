# backend/app/main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text 
from typing import List
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from . import auth 

# Importación de modelos, esquemas y configuración de base de datos
from . import models, schemas, database
from .dependencies import (
    get_current_user,
    get_owned_product,
    get_order_product,
    require_store_owner,
    require_user_without_store,
)

app = FastAPI(
    title="Especially API",
    description="Gestión de productos para emprendedores y artesanos",
    version="1.0.0"
)




# --- RUTAS DE CONSULTA (READ) ---

@app.get("/", tags=["General"])
def read_root():
    # Mensaje de bienvenida para confirmar que el contenedor está vivo
    return {"message": "Bienvenido a la API de Especially - Verde Jade activo"}

@app.get("/healthcheck", tags=["General"])
def health_check(db: Session = Depends(database.get_db)):
    # Verifica la integridad de la conexión con el contenedor PostgreSQL
    try:
        db.execute(text("SELECT 1"))
        return {"status": "online", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error de conexión a DB: {str(e)}")

@app.get("/products", response_model=List[schemas.Product], tags=["Marketplace"])
def get_products(db: Session = Depends(database.get_db)):
    # Recupera todos los productos (Camisetas, Mandalas, Biblias) de la base de datos
    products = db.query(models.Product).all()
    return products

# --- RUTAS DE CREACIÓN (WRITE) ---

@app.post("/products", response_model=schemas.Product, tags=["Marketplace"])
def create_product(
    product: schemas.ProductCreate, 
    db: Session = Depends(database.get_db),
    current_store: models.StoreProfile = Depends(require_store_owner),
):
    # 2. Creamos el producto usando el store_id de la marca de Bibiana (SoulsColors)
    db_product = models.Product(
        **product.model_dump(),
        store_id=current_store.store_id # <--- Aquí ocurre la vinculación automática
    )
    
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    return db_product

# --- RUTAS DE ELIMINACIÓN (DELETE) ---

@app.delete("/products/{product_id}", tags=["Marketplace"])
def delete_product(
    product: models.Product = Depends(get_owned_product),
    db: Session = Depends(database.get_db),
):
    db.delete(product)
    db.commit()
    return {"message": "Producto eliminado correctamente"}

# --- RUTAS DE ACTUALIZACIÓN (UPDATE) ---

@app.put("/products/{product_id}", response_model=schemas.Product, tags=["Marketplace"])
def update_product(
    product_data: schemas.ProductUpdate, 
    product: models.Product = Depends(get_owned_product),
    db: Session = Depends(database.get_db),
):
    update_data = product_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)

    db.commit()
    db.refresh(product)
    return product


# --- RUTA DE AUTENTICACIÓN (LOGIN) ---

@app.post("/token", response_model=schemas.Token, tags=["Seguridad"])
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    # 1. Buscar al usuario por email (usamos username porque así lo pide el estándar OAuth2)
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    
    # 2. Validar existencia y contraseña
    # Nota: Como tus datos actuales tienen 'hash_provisional', esto fallará 
    # hasta que registremos un usuario con hash real.
    if not user or not auth.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. Generar el Token
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users", response_model=schemas.User, tags=["Usuarios"])
def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    # 1. Verificar si el email ya existe
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")
    
    # 2. Cifrar la contraseña usando nuestra lógica en auth.py
    hashed_pass = auth.get_password_hash(user.password)
    
    # 3. Crear el nuevo usuario en la DB
    new_user = models.User(
        full_name=user.full_name,
        email=user.email,
        password_hash=hashed_pass, # Guardamos el hash, no la clave real
        user_role=user.user_role,
        city=user.city
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user




@app.post("/store", response_model=schemas.StoreProfile, tags=["Socio"])
def create_my_store(
    store_data: schemas.StoreProfileBase, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(require_user_without_store),
):
    # 2. Crear el perfil de SoulsColors o Fabio Hortua
    db_store = models.StoreProfile(
        **store_data.model_dump(),
        user_id=current_user.user_id
    )
    
    db.add(db_store)
    db.commit()
    db.refresh(db_store)
    return db_store


@app.post("/orders", response_model=schemas.OrderResponse, tags=["Orders"])
def create_order(
    order_data: schemas.OrderCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user),
    product: models.Product = Depends(get_order_product),
):
    # 2. Seguridad financiera: Calculamos el total en el backend, no confiamos en el cliente
    total_calculated = product.base_price * order_data.quantity

    # 3. Ensamblar el pedido con los datos de personalización
    new_order = models.Order(
        buyer_id=current_user.user_id,          # Sacado del token digital
        product_id=product.product_id,          # Lo que el cliente eligió
        quantity=order_data.quantity,
        total_price=total_calculated,           # Precio seguro
        custom_text=order_data.custom_text,     # Ej: "Para mi mamá con amor - Salmo 23"
        custom_image_url=order_data.custom_image_url # Ej: "https://s3.amazon.../logo.png"
        # Nota: 'status' nace como 'PENDING' por defecto según el modelo
    )

    # 4. Guardar la orden en la base de datos
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    return new_order
