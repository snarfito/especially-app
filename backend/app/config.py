"""
Especially API — Configuración centralizada (pydantic-settings).

Todas las variables de entorno son validadas al arrancar la aplicación.
La instancia singleton ``settings`` es importada por los módulos que la necesitan.

Desarrollador: Fredy Hortua <fredy.hortua@gmail.com>
Proyecto:      Especially — Marketplace colombiano de personalización y artesanías
"""
# app/config.py
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración tipada y validada cargada desde ``.env``.

    Cualquier variable obligatoria que falte o sea débil hace fallar el
    arranque de la aplicación, evitando que se ejecute con valores
    inseguros por defecto.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── Base de datos ────────────────────────────────────────────────────────
    DATABASE_URL: str

    # ── JWT ──────────────────────────────────────────────────────────────────
    # SECRET_KEY es OBLIGATORIA y debe tener al menos 32 caracteres.
    # Generar con: python -c "import secrets; print(secrets.token_urlsafe(64))"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # ── Cloudflare R2 ────────────────────────────────────────────────────────
    R2_ACCOUNT_ID: str = ""
    R2_ACCESS_KEY_ID: str = ""
    R2_SECRET_ACCESS_KEY: str = ""
    R2_BUCKET_NAME: str = ""
    R2_PUBLIC_URL: str = ""

    # ── Wompi ────────────────────────────────────────────────────────────────
    WOMPI_PUBLIC_KEY: str = ""
    WOMPI_PRIVATE_KEY: str = ""
    WOMPI_INTEGRITY_SECRET: str = ""
    WOMPI_EVENTS_SECRET: str = ""

    @field_validator("SECRET_KEY")
    @classmethod
    def _secret_key_must_be_strong(cls, value: str) -> str:
        """Rechaza SECRET_KEYs débiles, vacías o con valores placeholder.

        Args:
            value: Valor recibido para ``SECRET_KEY``.

        Returns:
            El mismo valor si pasa todas las validaciones.

        Raises:
            ValueError: Si la clave es muy corta o coincide con un placeholder
                conocido (CHANGE_ME, default insegura, etc.).
        """
        if not value or len(value) < 32:
            raise ValueError(
                "SECRET_KEY debe tener al menos 32 caracteres. "
                "Generar con: python -c \"import secrets; print(secrets.token_urlsafe(64))\""
            )

        weak_patterns = {
            "change_me",
            "changeme",
            "secret",
            "default",
            "tu_llave_secreta",
            "super_segura",
        }
        lowered = value.lower()
        if any(pattern in lowered for pattern in weak_patterns):
            raise ValueError(
                "SECRET_KEY parece ser un valor placeholder o débil. "
                "Generar una nueva con: python -c \"import secrets; print(secrets.token_urlsafe(64))\""
            )

        return value


settings = Settings()
