"""modelo_datos_completo_v2

Revision ID: 208354222ff1
Revises: a8b2d1f90d1d
Create Date: 2026-04-17 16:11:08.416370

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '208354222ff1'
down_revision: Union[str, Sequence[str], None] = 'a8b2d1f90d1d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── 1. Recrear orderstatus con valores en español ──────────────────────────
    # El enum viejo tiene valores en inglés (PENDING, PROCESSING, SHIPPED, COMPLETED)
    # Postgres no permite ALTER TYPE para cambiar valores, hay que recrearlo.
    op.execute("ALTER TABLE orders ALTER COLUMN status TYPE TEXT USING status::TEXT")
    op.execute("DROP TYPE IF EXISTS orderstatus")
    op.execute("""
        CREATE TYPE orderstatus AS ENUM (
            'pendiente', 'aceptado', 'produciendo', 'enviado', 'entregado', 'cancelado'
        )
    """)
    op.execute("""
        ALTER TABLE orders
        ALTER COLUMN status TYPE orderstatus
        USING 'pendiente'::orderstatus
    """)
    op.execute("ALTER TABLE orders ALTER COLUMN status SET NOT NULL")

    # ── 2. Crear shippingtype ──────────────────────────────────────────────────
    op.execute("""
        CREATE TYPE shippingtype AS ENUM ('normal', 'urgente')
    """)

    # ── 3. Modificar tabla orders ──────────────────────────────────────────────
    # Quitar constraint y columnas viejas
    op.drop_constraint('orders_product_id_fkey', 'orders', type_='foreignkey')
    op.drop_column('orders', 'product_id')
    op.drop_column('orders', 'quantity')
    op.drop_column('orders', 'total_price')
    op.drop_column('orders', 'custom_text')
    op.drop_column('orders', 'custom_image_url')

    # Agregar columnas nuevas (server_default temporal para pasar el NOT NULL con filas existentes)
    op.add_column('orders', sa.Column('shipping_type',
                  sa.Enum('normal', 'urgente', name='shippingtype'), nullable=True))
    op.add_column('orders', sa.Column('total_amount',
                  sa.Numeric(precision=12, scale=2), nullable=False,
                  server_default='0'))
    op.add_column('orders', sa.Column('shipping_address',
                  sa.Text(), nullable=False, server_default=''))

    # Quitar los server_defaults temporales
    op.alter_column('orders', 'total_amount', server_default=None)
    op.alter_column('orders', 'shipping_address', server_default=None)

    # Normalizar created_at a timezone-aware
    op.alter_column('orders', 'created_at',
                    existing_type=postgresql.TIMESTAMP(),
                    type_=sa.DateTime(timezone=True),
                    existing_nullable=True)

    # ── 4. Nuevas tablas ───────────────────────────────────────────────────────
    op.create_table('custom_designs',
        sa.Column('design_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=True),
        sa.Column('canvas_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('preview_image_url', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id']),
        sa.PrimaryKeyConstraint('design_id')
    )

    op.create_table('product_images',
        sa.Column('image_id', sa.UUID(), nullable=False),
        sa.Column('product_id', sa.UUID(), nullable=False),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('view_type', sa.String(length=30), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['product_id'], ['products.product_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('image_id')
    )

    # order_items al final: depende de custom_designs y orders
    op.create_table('order_items',
        sa.Column('item_id', sa.UUID(), nullable=False),
        sa.Column('order_id', sa.UUID(), nullable=False),
        sa.Column('product_id', sa.UUID(), nullable=False),
        sa.Column('design_id', sa.UUID(), nullable=True),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit_price', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('size', sa.String(length=10), nullable=True),
        sa.Column('garment_color', sa.String(length=30), nullable=True),
        sa.ForeignKeyConstraint(['design_id'], ['custom_designs.design_id']),
        sa.ForeignKeyConstraint(['order_id'], ['orders.order_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['product_id'], ['products.product_id']),
        sa.PrimaryKeyConstraint('item_id')
    )

    # ── 5. created_at en products ──────────────────────────────────────────────
    op.add_column('products',
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.text('now()'), nullable=True))


def downgrade() -> None:
    op.drop_column('products', 'created_at')
    op.drop_table('order_items')
    op.drop_table('product_images')
    op.drop_table('custom_designs')

    op.drop_column('orders', 'shipping_address')
    op.drop_column('orders', 'total_amount')
    op.drop_column('orders', 'shipping_type')
    op.execute("DROP TYPE IF EXISTS shippingtype")

    op.add_column('orders', sa.Column('quantity', sa.NUMERIC(), nullable=True))
    op.add_column('orders', sa.Column('product_id', sa.UUID(), nullable=False,
                  server_default='00000000-0000-0000-0000-000000000000'))
    op.add_column('orders', sa.Column('custom_text', sa.TEXT(), nullable=True))
    op.add_column('orders', sa.Column('total_price',
                  sa.NUMERIC(precision=12, scale=2), nullable=True))
    op.add_column('orders', sa.Column('custom_image_url',
                  sa.VARCHAR(length=500), nullable=True))
    op.create_foreign_key('orders_product_id_fkey', 'orders', 'products',
                          ['product_id'], ['product_id'])

    # Restaurar orderstatus en inglés
    op.execute("ALTER TABLE orders ALTER COLUMN status TYPE TEXT USING status::TEXT")
    op.execute("DROP TYPE IF EXISTS orderstatus")
    op.execute("""
        CREATE TYPE orderstatus AS ENUM ('PENDING', 'PROCESSING', 'SHIPPED', 'COMPLETED')
    """)
    op.execute("""
        ALTER TABLE orders
        ALTER COLUMN status TYPE orderstatus
        USING 'PENDING'::orderstatus
    """)
