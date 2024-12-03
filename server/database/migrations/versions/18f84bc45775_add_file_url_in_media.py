"""add file_url in media

Revision ID: 18f84bc45775
Revises: 0dafbb8add08
Create Date: 2024-11-23 15:33:33.692828

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "18f84bc45775"
down_revision: Union[str, None] = "0dafbb8add08"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column("medias", sa.Column("file_url", sa.String(), nullable=False))


def downgrade():
    op.drop_column("medias", "file_url")
