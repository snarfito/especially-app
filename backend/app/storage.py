# app/storage.py
"""
Especially API — Cliente de almacenamiento Cloudflare R2.

Usa boto3 con la API compatible S3 de R2. Centraliza todas las operaciones
de subida y eliminación de archivos (imágenes de productos, miniaturas de
diseños, PDFs de especificaciones).

Desarrollador: Fredy Hortua <fredy.hortua@gmail.com>
Proyecto:      Especially — Marketplace colombiano de personalización y artesanías
"""
import os
import uuid
from typing import Optional
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

R2_ACCOUNT_ID        = os.getenv("R2_ACCOUNT_ID")
R2_ACCESS_KEY_ID     = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
R2_BUCKET_NAME       = os.getenv("R2_BUCKET_NAME")
R2_PUBLIC_URL        = os.getenv("R2_PUBLIC_URL")  # https://pub-xxx.r2.dev

R2_ENDPOINT          = f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com"

# Cliente boto3 apuntando a R2
s3_client = boto3.client(
    "s3",
    endpoint_url=R2_ENDPOINT,
    aws_access_key_id=R2_ACCESS_KEY_ID,
    aws_secret_access_key=R2_SECRET_ACCESS_KEY,
    region_name="auto",
)


def upload_file(
    file_bytes: bytes,
    content_type: str,
    folder: str,
    filename: Optional[str] = None,
) -> str:
    """
    Sube un archivo a R2 y devuelve la URL pública.

    folder: carpeta dentro del bucket, ej: 'products', 'designs'
    filename: nombre del archivo. Si no se pasa, se genera un UUID.
    """
    if not filename:
        ext = content_type.split("/")[-1]  # image/jpeg → jpeg
        filename = f"{uuid.uuid4()}.{ext}"

    key = f"{folder}/{filename}"

    s3_client.put_object(
        Bucket=R2_BUCKET_NAME,
        Key=key,
        Body=file_bytes,
        ContentType=content_type,
    )

    # Devuelve URL pública directa (bucket con Public Development URL habilitado)
    return f"{R2_PUBLIC_URL}/{key}"


def delete_file(key: str) -> None:
    """Elimina un archivo del bucket por su key."""
    try:
        s3_client.delete_object(Bucket=R2_BUCKET_NAME, Key=key)
    except ClientError:
        pass  # Si no existe, no es un error crítico
