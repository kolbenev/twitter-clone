"""add media

Revision ID: 0dafbb8add08
Revises: 72c0204ee7e7
Create Date: 2024-11-22 12:56:07.039066

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0dafbb8add08'
down_revision: Union[str, None] = '72c0204ee7e7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('media',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('file_path', sa.String(), nullable=False),
    sa.Column('tweet_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['tweet_id'], ['tweets.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.alter_column('tweets', 'author_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('tweets', 'author_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.drop_table('media')
    # ### end Alembic commands ###
