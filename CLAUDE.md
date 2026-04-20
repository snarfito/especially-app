# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Especially is a Colombian marketplace for personalized products and artisan crafts. It is a monorepo with two independent services:

- `backend/` — FastAPI + PostgreSQL REST API (Python)
- `frontend/` — Next.js 16 App Router (TypeScript + Tailwind CSS)

## Commands

### Backend

```bash
# Start the database (PostgreSQL on port 5432, pgAdmin on port 5050)
docker-compose up -d

# Install dependencies (from backend/)
cd backend && pip install -r requirements.txt

# Run the API server (from backend/)
uvicorn app.main:app --reload

# Run database migrations
cd backend && alembic upgrade head

# Create a new migration after changing models.py
cd backend && alembic revision --autogenerate -m "description"

# Run tests
cd backend && python -m unittest discover tests

# Run a single test
cd backend && python -m unittest tests.test_authorization.TestDependencies.test_name
```

### Frontend

```bash
# Install dependencies (from frontend/)
cd frontend && npm install

# Start the dev server (localhost:3000)
cd frontend && npm run dev

# Build for production
cd frontend && npm run build

# Lint
cd frontend && npm run lint
```

## Architecture

### Backend

**Entry point:** `backend/app/main.py` — creates the FastAPI app, mounts all routers, configures CORS for `localhost:3000` and `localhost:5173`.

**Layer structure:**
- `routers/` — HTTP endpoints, one file per domain (auth, stores, products, images, orders, designs, payments). Routers inject dependencies and delegate data access to `crud.py`.
- `crud.py` — All database reads/writes. Routers never call the ORM directly.
- `models.py` — SQLAlchemy ORM with UUID PKs throughout. All tables use `uuid-ossp`.
- `schemas.py` — Pydantic v2 schemas using `Base/Create/Update/Response` naming convention.
- `dependencies.py` — Reusable FastAPI `Depends` helpers: `get_current_user`, `require_role`, `get_or_404`.
- `auth.py` — JWT (HS256, 60-min expiry) via `python-jose`; password hashing via `passlib[bcrypt]`.
- `storage.py` — Cloudflare R2 client (S3-compatible, boto3). Uploads to `products/`, `designs/`, `specs/` prefixes.
- `pdf_generator.py` — ReportLab spec sheet generation, result uploaded to R2.
- `config.py` — Pydantic `Settings` class; reads `.env` automatically.

**Auth flow:** OAuth2 password → `POST /token` → JWT Bearer token. All protected routes use `Depends(get_current_user)`. Role enforcement via `Depends(require_role("seller"))`.

**Local dev port:** the API runs on `http://localhost:8001` (frontend reads `NEXT_PUBLIC_API_URL` from `.env.local`). Start with `uvicorn app.main:app --reload --port 8001`.

**Roles:** `buyer`, `socio_productor` (seller), `designer`.

**Payments:** Wompi (Colombian gateway). `GET /payments/integrity-signature` returns SHA256 signature for the Wompi widget. `POST /payments/webhook` handles transaction events and updates order `payment_status`.

### Frontend

**Entry point:** `frontend/src/app/layout.tsx` — root layout wrapping all pages with `<Navbar>`.

**Route groups (Next.js App Router):**
- `(auth)/login`, `(auth)/registro` — Authentication pages
- `(buyer)/catalogo`, `(buyer)/carrito` — Buyer-facing pages
- `(seller)/dashboard` — Seller dashboard

**Shared libraries:**
- `lib/api.ts` — Fetch wrapper that reads JWT from `localStorage` and injects `Authorization: Bearer` header. All API calls go through this.
- `lib/auth.ts` — Helpers to read/write JWT and user data to `localStorage`.
- `types/index.ts` — Single source of truth for all TypeScript types.

**Styling:** Tailwind CSS v4 with a custom `jade-*` color palette defined in `globals.css`.

### Database

PostgreSQL 15. Schema managed with Alembic. Key tables: `users`, `store_profiles`, `products`, `product_images`, `custom_designs`, `orders`, `order_items`.

The `orders` table tracks both `status` (OrderStatus enum: pending → accepted → producing → shipped → delivered/cancelled) and `payment_status` (PaymentStatus enum: pending → paid/pago_fallido/refunded) independently.

Local DB: `postgresql+psycopg://admin:password123@localhost:5432/especially_v1` (from `docker-compose.yml`).

### Environment Variables

**Backend (`backend/.env`):** `DATABASE_URL`, `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET_NAME`, `R2_PUBLIC_URL`, `WOMPI_PUBLIC_KEY`, `WOMPI_PRIVATE_KEY`, `WOMPI_INTEGRITY_SECRET`, `WOMPI_EVENTS_SECRET`.

**Frontend (`frontend/.env.local`):** `NEXT_PUBLIC_API_URL=http://localhost:8001`.

## Code Documentation Standards

These rules apply to all Python files in the backend.

**Module docstrings** — every file must open with a docstring that includes author and project:

```python
"""
Brief description of this module.

Author: Fredy Hortua <fredy.hortua@gmail.com>
Project: Especially
"""
# app/nombre.py
```

The `# app/nombre.py` path comment goes **after** the docstring, never before it.

**Router modules** must also list their endpoints in the module docstring:

```python
"""
Gestión de productos del catálogo.

Endpoints:
    GET  /products        - Listar productos (paginado, filtrable)
    POST /products        - Crear producto (solo vendedor)
    PUT  /products/{id}   - Actualizar producto
    DELETE /products/{id} - Eliminar producto

Author: Fredy Hortua <fredy.hortua@gmail.com>
Project: Especially
"""
# app/routers/products.py
```

**Function docstrings** — every public function uses Google style with `Args` and `Returns` sections:

```python
def create_product(db: Session, product: ProductCreate, seller_id: UUID) -> Product:
    """Crea un nuevo producto asociado a una tienda.

    Args:
        db: Sesión activa de SQLAlchemy.
        product: Datos validados del nuevo producto.
        seller_id: UUID del vendedor dueño del producto.

    Returns:
        El objeto Product recién creado y persistido.
    """
```

**Module-level variables** always carry explicit type hints:

```python
router: APIRouter = APIRouter(prefix="/products", tags=["products"])
pwd_context: CryptContext = CryptContext(schemes=["bcrypt"])
```

No public function may be left without a docstring.

## Key Conventions

- All primary keys are UUIDs (`uuid-ossp` extension).
- Backend Pydantic schemas follow `{Entity}Base / {Entity}Create / {Entity}Update / {Entity}Response` pattern.
- Frontend uses `"use client"` directive for all interactive components; static pages are server components by default.
- The Swagger UI is available at `http://localhost:8000/docs` when the backend is running.
