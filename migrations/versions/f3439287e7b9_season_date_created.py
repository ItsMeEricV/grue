"""season date_created

Revision ID: f3439287e7b9
Revises: b53e9e6b128a
Create Date: 2024-11-26 06:31:58.220074

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f3439287e7b9'
down_revision = 'b53e9e6b128a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('seasons', schema=None) as batch_op:
        batch_op.add_column(sa.Column('date_created', postgresql.TIMESTAMP(timezone=True), server_default='now()', nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('seasons', schema=None) as batch_op:
        batch_op.drop_column('date_created')

    # ### end Alembic commands ###
