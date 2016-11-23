"""add front selection

Revision ID: 498ae3ad284e
Revises: 4a5bf96b558d
Create Date: 2016-11-22 19:02:18.223553

"""

# revision identifiers, used by Alembic.
revision = '498ae3ad284e'
down_revision = '4a5bf96b558d'

from alembic import op
import sqlalchemy as sa


def upgrade():
    front_projects_table = op.create_table(
        'front_projects',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('well', sa.Integer),
        sa.Column('tag', sa.Integer),
        sa.ForeignKeyConstraint(['tag'], ['tags.id'])
    )


def downgrade():
    op.drop_table('front_projects')
