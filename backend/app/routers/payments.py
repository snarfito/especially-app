"""
Especially API — Router de pagos (integración Wompi).

Endpoints:
  GET  /payments/integrity-signature  → Genera la firma SHA256 para el widget de pago.
  POST /payments/webhook              → Recibe eventos de Wompi (transacción aprobada/rechazada).

Desarrollador: Fredy Hortua <fredy.hortua@gmail.com>
Proyecto:      Especially — Marketplace colombiano de personalización y artesanías
"""
# app/routers/payments.py
import hashlib
import hmac
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user
from .. import crud, models, schemas
from ..config import settings

router: APIRouter = APIRouter(prefix="/payments", tags=["Pagos"])


# ─── 1. Firma de integridad ───────────────────────────────────────────────────
# El frontend la necesita antes de abrir el widget de Wompi.
# Wompi exige: SHA256( reference + amount_in_cents + currency + INTEGRITY_SECRET )

@router.get("/integrity-signature")
def get_integrity_signature(
    order_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Devuelve la firma de integridad para una orden específica del usuario autenticado.
    El frontend pasa order_id y recibe los parámetros listos para el widget.
    """
    order = crud.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    if order.buyer_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Acceso denegado")
    if order.payment_status == "pagado":
        raise HTTPException(status_code=400, detail="Esta orden ya fue pagada")

    # Wompi trabaja en centavos (enteros), sin decimales
    amount_in_cents = int(order.total_amount * 100)
    currency = "COP"
    reference = order.payment_reference

    raw_string = f"{reference}{amount_in_cents}{currency}{settings.WOMPI_INTEGRITY_SECRET}"
    signature = hashlib.sha256(raw_string.encode("utf-8")).hexdigest()

    return {
        "public_key":      settings.WOMPI_PUBLIC_KEY,
        "reference":       reference,
        "amount_in_cents": amount_in_cents,
        "currency":        currency,
        "signature":       signature,
    }


# ─── 2. Webhook ───────────────────────────────────────────────────────────────
# Wompi hace POST aquí cada vez que una transacción cambia de estado.
# ESTA es la fuente de verdad — nunca usar el redirect del frontend para marcar pagos.

@router.post("/webhook", status_code=status.HTTP_200_OK)
async def wompi_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Recibe eventos de Wompi. Valida la firma SHA256 del evento y actualiza
    el estado de la orden según el resultado de la transacción.
    """
    raw_body = await request.body()
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="JSON inválido")

    # ── Validar firma del evento ──────────────────────────────────────────────
    # Wompi concatena: valores de 'properties' (en orden) + timestamp + EVENTS_SECRET
    try:
        sig_data   = payload["signature"]
        properties = sig_data["properties"]   # e.g. ["transaction.id", "transaction.status", "transaction.amount_in_cents"]
        timestamp  = payload["timestamp"]
        checksum   = sig_data.get("checksum") or request.headers.get("X-Event-Checksum", "")

        data_obj = payload["data"]
        values = []
        for prop in properties:
            # Navega rutas tipo "transaction.status" → data["transaction"]["status"]
            keys = prop.split(".")
            val = data_obj
            for k in keys:
                val = val[k]
            values.append(str(val))

        concat = "".join(values) + str(timestamp) + settings.WOMPI_EVENTS_SECRET
        expected = hashlib.sha256(concat.encode("utf-8")).hexdigest()

        if not hmac.compare_digest(expected.upper(), checksum.upper()):
            raise HTTPException(status_code=401, detail="Firma inválida")

    except HTTPException:
        raise
    except (KeyError, TypeError) as e:
        raise HTTPException(status_code=400, detail=f"Payload mal formado: {e}")

    # ── Procesar el evento ────────────────────────────────────────────────────
    event_type  = payload.get("event")
    transaction = payload.get("data", {}).get("transaction", {})

    if event_type == "transaction.updated":
        reference = transaction.get("reference")
        tx_status = transaction.get("status")       # APPROVED | DECLINED | VOIDED | ERROR
        wompi_id  = transaction.get("id")

        order = crud.get_order_by_payment_reference(db, reference)
        if order:
            if tx_status == "APPROVED":
                crud.update_order_payment(db, order, payment_status="pagado", wompi_transaction_id=wompi_id)
                # Aquí después: disparar notificación al productor, enviar email, etc.
            elif tx_status in ("DECLINED", "VOIDED", "ERROR"):
                crud.update_order_payment(db, order, payment_status="pago_fallido", wompi_transaction_id=wompi_id)

    # Wompi espera 200 rápido — si tardamos más de ~10s reintenta
    return {"status": "ok"}
