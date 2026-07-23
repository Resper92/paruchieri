"""add role enum to users

Revision ID: a1b2c3d4e5f6
Revises: eb41776c5c75
Create Date: 2026-07-22 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = "a1b2c3d4e5f6"
down_revision = "eb41776c5c75"
branch_labels = None
depends_on = None

ROLE_VALUES = ("superadmin", "parrucchiere", "client")


def upgrade() -> None:
    op.execute(
        "UPDATE users SET role = 'client' "
        "WHERE role IS NULL OR role NOT IN ('superadmin', 'parrucchiere', 'client')"
    )
    role_enum = sa.Enum(*ROLE_VALUES, name="role", native_enum=False)
    op.alter_column(
        "users",
        "role",
        existing_type=sa.String(),
        type_=role_enum,
        nullable=False,
        server_default="client",
    )
    op.create_check_constraint(
        "ck_users_role",
        "users",
        sa.column("role").in_(ROLE_VALUES),
    )


def downgrade() -> None:
    op.drop_constraint("ck_users_role", "users", type_="check")
    op.alter_column(
        "users",
        "role",
        existing_type=sa.Enum(*ROLE_VALUES, name="role", native_enum=False),
        type_=sa.String(),
        nullable=True,
        server_default=None,
    )
