"""add spec_pdf_url and wompi fields to orders

Revision ID: b3c8e2f10a5d
Revises: 208354222ff1
Create Date: 2026-04-19 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b3c8e2f10a5d'
down_revision = '208354222ff1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Campos de pago Wompi (si no existen aún)
    conn = op.get_bind()
    existing_cols = {row[0] for row in conn.execute(
        sa.text("SELECT column_name FROM information_schema.columns WHERE table_name='orders'")
    )}

    if 'payment_reference' not in existing_cols:
        op.add_column('orders', sa.Column('payment_reference', sa.String(100), nullable=True, unique=True))
        op.create_index('ix_orders_payment_reference', 'orders', ['payment_reference'], unique=True)

    if 'payment_status' not in existing_cols:
        op.add_column('orders', sa.Column('payment_status', sa.String(20), nullable=False, server_default='pendiente'))

    if 'wompi_transaction_id' not in existing_cols:
        op.add_column('orders', sa.Column('wompi_transaction_id', sa.String(100), nullable=True))

    # URL del PDF de especificaciones en R2
    if 'spec_pdf_url' not in existing_cols:
        op.add_column('orders', sa.Column('spec_pdf_url', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('orders', 'spec_pdf_url')
    op.drop_index('ix_orders_payment_reference', table_name='orders')
    op.drop_column('orders', 'payment_reference')
    op.drop_column('orders', 'payment_status')
    op.drop_column('orders', 'wompi_transaction_id')
