from alembic import op
import sqlalchemy as sa


revision = "20251007_000001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "buildings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("address", sa.String(length=255), nullable=False, index=True),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
    )

    op.create_table(
        "activities",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False, unique=True, index=True),
        sa.Column("parent_id", sa.Integer(), sa.ForeignKey("activities.id"), nullable=True),
    )

    op.create_table(
        "organizations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False, index=True),
        sa.Column("building_id", sa.Integer(), sa.ForeignKey("buildings.id"), nullable=False, index=True),
    )

    op.create_table(
        "phones",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("number", sa.String(length=50), nullable=False),
        sa.Column("organization_id", sa.Integer(), sa.ForeignKey("organizations.id"), nullable=False, index=True),
    )

    op.create_table(
        "organization_activity",
        sa.Column("organization_id", sa.Integer(), sa.ForeignKey("organizations.id"), primary_key=True),
        sa.Column("activity_id", sa.Integer(), sa.ForeignKey("activities.id"), primary_key=True),
    )


def downgrade() -> None:
    op.drop_table("organization_activity")
    op.drop_table("phones")
    op.drop_table("organizations")
    op.drop_table("activities")
    op.drop_table("buildings")


