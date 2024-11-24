"""constraint and location index

Revision ID: b53e9e6b128a
Revises: e45a0feee25c
Create Date: 2024-11-24 19:48:23.009338

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b53e9e6b128a'
down_revision = 'e45a0feee25c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('locations', schema=None) as batch_op:
        batch_op.create_index('ix_locations_season_id', ['season_id'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('locations', schema=None) as batch_op:
        batch_op.drop_index('ix_locations_season_id')

    # ### end Alembic commands ###