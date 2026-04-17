"""add seller_id to orders

Revision ID: 9c3f5d4c2a11
Revises: a46ff09b3c1d
Create Date: 2026-03-28 12:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9c3f5d4c2a11"
down_revision: Union[str, Sequence[str], None] = "a46ff09b3c1d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("orders", sa.Column("seller_id", sa.UUID(), nullable=True))
    op.create_foreign_key(
        "fk_orders_seller_id_users",
        "orders",
        "users",
        ["seller_id"],
        ["user_id"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_orders_seller_id_users", "orders", type_="foreignkey")
    op.drop_column("orders", "seller_id")
