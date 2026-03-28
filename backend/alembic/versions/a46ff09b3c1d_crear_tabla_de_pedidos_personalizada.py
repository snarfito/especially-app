"""crear tabla de pedidos personalizada

Revision ID: a46ff09b3c1d
Revises: e5f737a3335f
Create Date: 2026-03-28 00:14:55.245806

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a46ff09b3c1d'
down_revision: Union[str, Sequence[str], None] = 'e5f737a3335f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Deja que SQLAlchemy lo cree solo al definir la tabla abajo
    op.create_table('orders',
        sa.Column('order_id', sa.UUID(), nullable=False),
        sa.Column('buyer_id', sa.UUID(), nullable=False),
        sa.Column('product_id', sa.UUID(), nullable=False),
        sa.Column('quantity', sa.Numeric(), nullable=True),
        sa.Column('total_price', sa.Numeric(precision=12, scale=2), nullable=True),
        # Aquí es donde SQLAlchemy detecta que debe crear el tipo 'orderstatus'
        sa.Column('status', sa.Enum('PENDING', 'PROCESSING', 'SHIPPED', 'COMPLETED', name='orderstatus'), nullable=True),
        sa.Column('custom_text', sa.Text(), nullable=True),
        sa.Column('custom_image_url', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['buyer_id'], ['users.user_id'], ),
        sa.ForeignKeyConstraint(['product_id'], ['products.product_id'], ),
        sa.PrimaryKeyConstraint('order_id')
    )

def downgrade() -> None:
    op.drop_table('orders')
    sa.Enum(name='orderstatus').drop(op.get_bind())

