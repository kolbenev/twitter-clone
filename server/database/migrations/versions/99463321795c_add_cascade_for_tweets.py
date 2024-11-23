"""add cascade for tweets

Revision ID: 99463321795c
Revises: 18f84bc45775
Create Date: 2024-11-23 19:24:19.363320

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '99463321795c'
down_revision: Union[str, None] = '18f84bc45775'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.drop_constraint('likes_tweet_id_fkey', 'likes', type_='foreignkey')
    op.create_foreign_key(
        'likes_tweet_id_fkey',
        'likes',
        'tweets',
        ['tweet_id'],
        ['id'],
        ondelete='CASCADE'
    )

    op.drop_constraint('medias_tweet_id_fkey', 'medias', type_='foreignkey')
    op.create_foreign_key(
        'medias_tweet_id_fkey',
        'medias',
        'tweets',
        ['tweet_id'],
        ['id'],
        ondelete='CASCADE'
    )


def downgrade():
    op.drop_constraint('likes_tweet_id_fkey', 'likes', type_='foreignkey')
    op.create_foreign_key(
        'likes_tweet_id_fkey',
        'likes',
        'tweets',
        ['tweet_id'],
        ['id'],
        ondelete=None
    )

    op.drop_constraint('medias_tweet_id_fkey', 'medias', type_='foreignkey')
    op.create_foreign_key(
        'medias_tweet_id_fkey',
        'medias',
        'tweets',
        ['tweet_id'],
        ['id'],
        ondelete=None
    )
