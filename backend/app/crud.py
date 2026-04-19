"""
Especially API — Capa de acceso a datos (CRUD).

Centraliza toda la lógica de consulta y mutación sobre la base de datos.
Ningún router debe ejecutar consultas directamente; todo pasa por aquí.

Secciones:
  - Usuarios       → get_user_by_email, get_user_by_id, create_user
  - Tiendas        → create_store, get_store_by_user
  - Productos      → get_products, get_product_by_id, create_product,
                      update_product, delete_product
  - Pedidos        → create_order, get_orders_by_buyer, get_order_by_id,
                      get_pending_orders, assign_order_to_seller,
                      update_order_status
  - Diseños        → create_custom_design, get_design_by_id,
                      get_designs_by_user, delete_custom_design
  - Pagos / Wompi  → get_order_by_payment_reference, update_order_payment
  - Imágenes       → create_product_image, get_product_images,
                      get_product_image_by_id, delete_product_image

Desarrollador: Fredy Hortua <fredy.hortua@gmail.com>
Proyecto:      Especially — Marketplace colombiano de personalización y artesanías
"""
# app/crud.py
from decimal import Decimal
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from . import models, schemas
from .auth import get_password_hash


# ─── USUARIOS ─────────────────────────────────────────────────────────────────

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Busca un usuario por su dirección de correo electrónico.

    Args:
        db: Sesión activa de SQLAlchemy.
        email: Correo del usuario a buscar.

    Returns:
        Instancia de ``User`` si existe, ``None`` en caso contrario.
    """
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_id(db: Session, user_id: UUID) -> Optional[models.User]:
    """Busca un usuario por su UUID primario.

    Args:
        db: Sesión activa de SQLAlchemy.
        user_id: Identificador único del usuario.

    Returns:
        Instancia de ``User`` si existe, ``None`` en caso contrario.
    """
    return db.query(models.User).filter(models.User.user_id == user_id).first()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Crea un nuevo usuario hasheando su contraseña antes de persistir.

    Args:
        db: Sesión activa de SQLAlchemy.
        user: Datos validados del nuevo usuario.

    Returns:
        Instancia de ``User`` recién creada y refrescada desde la DB.
    """
    db_user = models.User(
        full_name=user.full_name,
        email=user.email,
        password_hash=get_password_hash(user.password),
        user_role=user.user_role,
        city=user.city,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# ─── TIENDAS ──────────────────────────────────────────────────────────────────

def create_store(
    db: Session,
    store_data: schemas.StoreProfileBase,
    user_id: UUID,
) -> models.StoreProfile:
    """Crea un perfil de tienda asociado a un usuario.

    Args:
        db: Sesión activa de SQLAlchemy.
        store_data: Datos del perfil comercial.
        user_id: UUID del usuario propietario.

    Returns:
        Instancia de ``StoreProfile`` recién creada.
    """
    db_store = models.StoreProfile(
        **store_data.model_dump(),
        user_id=user_id,
    )
    db.add(db_store)
    db.commit()
    db.refresh(db_store)
    return db_store


def get_store_by_user(db: Session, user_id: UUID) -> Optional[models.StoreProfile]:
    """Devuelve el perfil de tienda de un usuario, si existe.

    Args:
        db: Sesión activa de SQLAlchemy.
        user_id: UUID del usuario propietario.

    Returns:
        Instancia de ``StoreProfile`` o ``None``.
    """
    return db.query(models.StoreProfile).filter(
        models.StoreProfile.user_id == user_id
    ).first()


# ─── PRODUCTOS ────────────────────────────────────────────────────────────────

def get_products(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    category: Optional[str] = None,
) -> List[models.Product]:
    """Devuelve la lista paginada de productos, con filtro opcional por categoría.

    Args:
        db: Sesión activa de SQLAlchemy.
        skip: Número de registros a omitir (paginación).
        limit: Máximo de registros a retornar.
        category: Si se provee, filtra por categoría exacta.

    Returns:
        Lista de instancias de ``Product``.
    """
    query = db.query(models.Product)
    if category:
        query = query.filter(models.Product.category == category)
    return query.offset(skip).limit(limit).all()


def get_product_by_id(db: Session, product_id: UUID) -> Optional[models.Product]:
    """Busca un producto por su UUID.

    Args:
        db: Sesión activa de SQLAlchemy.
        product_id: Identificador único del producto.

    Returns:
        Instancia de ``Product`` o ``None``.
    """
    return db.query(models.Product).filter(
        models.Product.product_id == product_id
    ).first()


def create_product(
    db: Session,
    product: schemas.ProductCreate,
    store_id: UUID,
) -> models.Product:
    """Crea un producto asociado a una tienda.

    Args:
        db: Sesión activa de SQLAlchemy.
        product: Datos validados del nuevo producto.
        store_id: UUID de la tienda propietaria.

    Returns:
        Instancia de ``Product`` recién creada.
    """
    db_product = models.Product(
        **product.model_dump(),
        store_id=store_id,
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def update_product(
    db: Session,
    product: models.Product,
    product_data: schemas.ProductUpdate,
) -> models.Product:
    """Actualiza parcialmente los campos de un producto existente.

    Solo modifica los campos incluidos en ``product_data`` (exclude_unset).

    Args:
        db: Sesión activa de SQLAlchemy.
        product: Instancia ORM del producto a modificar.
        product_data: Campos a actualizar (todos opcionales).

    Returns:
        Instancia de ``Product`` actualizada.
    """
    for key, value in product_data.model_dump(exclude_unset=True).items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product: models.Product) -> None:
    """Elimina un producto de la base de datos.

    Args:
        db: Sesión activa de SQLAlchemy.
        product: Instancia ORM del producto a eliminar.
    """
    db.delete(product)
    db.commit()


# ─── PEDIDOS ──────────────────────────────────────────────────────────────────

def create_order(
    db: Session,
    order_data: schemas.OrderCreate,
    buyer_id: UUID,
) -> models.Order:
    """
    Crea una orden con sus items. Calcula el total sumando
    base_price * quantity de cada producto en la DB (nunca confía en el cliente).
    """
    total = Decimal("0")
    items_to_create = []

    for item_data in order_data.items:
        product = get_product_by_id(db, item_data.product_id)
        if not product:
            raise ValueError(f"Producto {item_data.product_id} no encontrado")

        unit_price = product.base_price
        total += unit_price * item_data.quantity

        items_to_create.append(models.OrderItem(
            product_id=item_data.product_id,
            design_id=item_data.design_id,
            quantity=item_data.quantity,
            unit_price=unit_price,
            size=item_data.size,
            garment_color=item_data.garment_color,
        ))

    db_order = models.Order(
        buyer_id=buyer_id,
        seller_id=None,
        status=models.OrderStatus.PENDING,
        shipping_type=order_data.shipping_type,
        total_amount=total,
        shipping_address=order_data.shipping_address,
        payment_reference=f"ESP-{uuid4().hex[:12].upper()}",  # referencia única para Wompi
        payment_status="pendiente",
    )
    db.add(db_order)
    db.flush()  # genera order_id sin commit para asociar los items

    for item in items_to_create:
        item.order_id = db_order.order_id
        db.add(item)

    db.commit()
    db.expire(db_order)  # fuerza releer created_at generado por el servidor
    db.refresh(db_order)
    return db_order


def get_orders_by_buyer(
    db: Session,
    buyer_id: UUID,
) -> List[models.Order]:
    """Devuelve todos los pedidos de un comprador, ordenados por fecha descendente.

    Args:
        db: Sesión activa de SQLAlchemy.
        buyer_id: UUID del comprador.

    Returns:
        Lista de instancias de ``Order``.
    """
    return (
        db.query(models.Order)
        .filter(models.Order.buyer_id == buyer_id)
        .order_by(models.Order.created_at.desc())
        .all()
    )


def get_order_by_id(db: Session, order_id: UUID) -> Optional[models.Order]:
    """Busca una orden por su UUID.

    Args:
        db: Sesión activa de SQLAlchemy.
        order_id: Identificador único de la orden.

    Returns:
        Instancia de ``Order`` o ``None``.
    """
    return db.query(models.Order).filter(
        models.Order.order_id == order_id
    ).first()


def get_pending_orders(db: Session) -> List[models.Order]:
    """Devuelve pedidos pendientes sin un socio asignado."""
    return (
        db.query(models.Order)
        .filter(models.Order.status == models.OrderStatus.PENDING)
        .filter(models.Order.seller_id.is_(None))
        .order_by(models.Order.created_at.desc())
        .all()
    )


def assign_order_to_seller(
    db: Session,
    order: models.Order,
    seller_id: UUID,
) -> models.Order:
    """Asigna un socio productor a una orden y la marca como aceptada.

    Args:
        db: Sesión activa de SQLAlchemy.
        order: Instancia ORM de la orden a asignar.
        seller_id: UUID del socio que acepta la orden.

    Returns:
        Instancia de ``Order`` actualizada.
    """
    order.seller_id = seller_id
    order.status = models.OrderStatus.ACCEPTED
    db.commit()
    db.refresh(order)
    return order


def update_order_status(
    db: Session,
    order: models.Order,
    new_status: models.OrderStatus,
) -> models.Order:
    """Actualiza el estado de flujo de una orden.

    Args:
        db: Sesión activa de SQLAlchemy.
        order: Instancia ORM de la orden.
        new_status: Nuevo estado del ciclo de vida (``OrderStatus``).

    Returns:
        Instancia de ``Order`` actualizada.
    """
    order.status = new_status
    db.commit()
    db.refresh(order)
    return order


# ─── DISEÑOS PERSONALIZADOS ───────────────────────────────────────────────────

def create_custom_design(
    db: Session,
    design_data: schemas.CustomDesignCreate,
    user_id: UUID,
) -> models.CustomDesign:
    """Persiste el estado del canvas de Fabric.js como diseño personalizado.

    Args:
        db: Sesión activa de SQLAlchemy.
        design_data: JSON del canvas y URL de miniatura (opcional).
        user_id: UUID del usuario propietario del diseño.

    Returns:
        Instancia de ``CustomDesign`` recién creada.
    """
    db_design = models.CustomDesign(
        user_id=user_id,
        canvas_json=design_data.canvas_json,
        preview_image_url=design_data.preview_image_url,
    )
    db.add(db_design)
    db.commit()
    db.refresh(db_design)
    return db_design


def get_design_by_id(db: Session, design_id: UUID) -> Optional[models.CustomDesign]:
    """Busca un diseño personalizado por su UUID.

    Args:
        db: Sesión activa de SQLAlchemy.
        design_id: Identificador único del diseño.

    Returns:
        Instancia de ``CustomDesign`` o ``None``.
    """
    return db.query(models.CustomDesign).filter(
        models.CustomDesign.design_id == design_id
    ).first()


def get_designs_by_user(
    db: Session,
    user_id: UUID,
) -> List[models.CustomDesign]:
    """Devuelve todos los diseños de un usuario, ordenados por fecha descendente.

    Args:
        db: Sesión activa de SQLAlchemy.
        user_id: UUID del usuario propietario.

    Returns:
        Lista de instancias de ``CustomDesign``.
    """
    return (
        db.query(models.CustomDesign)
        .filter(models.CustomDesign.user_id == user_id)
        .order_by(models.CustomDesign.created_at.desc())
        .all()
    )


def delete_custom_design(db: Session, design: models.CustomDesign) -> None:
    """Elimina un diseño personalizado de la base de datos.

    Args:
        db: Sesión activa de SQLAlchemy.
        design: Instancia ORM del diseño a eliminar.
    """
    db.delete(design)
    db.commit()


# ─── PAGOS / WOMPI ───────────────────────────────────────────────────────────

def get_order_by_payment_reference(
    db: Session,
    reference: str,
) -> Optional[models.Order]:
    """Busca una orden por su referencia única de pago (usada por el webhook de Wompi)."""
    return db.query(models.Order).filter(
        models.Order.payment_reference == reference
    ).first()


def update_order_payment(
    db: Session,
    order: models.Order,
    payment_status: str,
    wompi_transaction_id: Optional[str] = None,
) -> models.Order:
    """Actualiza el estado de pago de la orden tras recibir el evento de Wompi."""
    order.payment_status = payment_status
    if wompi_transaction_id:
        order.wompi_transaction_id = wompi_transaction_id
    db.commit()
    db.refresh(order)
    return order


# ─── IMÁGENES DE PRODUCTO ─────────────────────────────────────────────────────

def create_product_image(
    db: Session,
    image_data: schemas.ProductImageCreate,
    product_id: UUID,
) -> models.ProductImage:
    """Registra una imagen de producto en la base de datos.

    La imagen ya debe haber sido subida a R2 antes de llamar esta función.

    Args:
        db: Sesión activa de SQLAlchemy.
        image_data: URL, tipo de vista y orden de display.
        product_id: UUID del producto al que pertenece la imagen.

    Returns:
        Instancia de ``ProductImage`` recién creada.
    """
    db_image = models.ProductImage(
        product_id=product_id,
        url=image_data.url,
        view_type=image_data.view_type,
        display_order=image_data.display_order,
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image


def get_product_images(
    db: Session,
    product_id: UUID,
) -> List[models.ProductImage]:
    """Devuelve todas las imágenes de un producto ordenadas por ``display_order``.

    Args:
        db: Sesión activa de SQLAlchemy.
        product_id: UUID del producto.

    Returns:
        Lista de instancias de ``ProductImage``.
    """
    return (
        db.query(models.ProductImage)
        .filter(models.ProductImage.product_id == product_id)
        .order_by(models.ProductImage.display_order)
        .all()
    )


def get_product_image_by_id(
    db: Session,
    image_id: UUID,
) -> Optional[models.ProductImage]:
    """Busca una imagen de producto por su UUID.

    Args:
        db: Sesión activa de SQLAlchemy.
        image_id: Identificador único de la imagen.

    Returns:
        Instancia de ``ProductImage`` o ``None``.
    """
    return db.query(models.ProductImage).filter(
        models.ProductImage.image_id == image_id
    ).first()


def delete_product_image(db: Session, image: models.ProductImage) -> None:
    """Elimina el registro de una imagen de producto.

    Nota: la eliminación del archivo en R2 es responsabilidad del router.

    Args:
        db: Sesión activa de SQLAlchemy.
        image: Instancia ORM de la imagen a eliminar.
    """
    db.delete(image)
    db.commit()
