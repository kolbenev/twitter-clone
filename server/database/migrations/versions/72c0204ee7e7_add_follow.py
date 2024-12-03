"""add follow

Revision ID: 72c0204ee7e7
Revises: 75161a9bdacd
Create Date: 2024-11-22 12:51:11.385419

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "72c0204ee7e7"
down_revision: Union[str, None] = "75161a9bdacd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "follows",
        sa.Column("follower_id", sa.Integer(), nullable=False),
        sa.Column("following_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["follower_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["following_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("follower_id", "following_id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("follows")
    # ### end Alembic commands ###
