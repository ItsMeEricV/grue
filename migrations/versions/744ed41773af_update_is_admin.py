"""update is_admin

Revision ID: 744ed41773af
Revises: ff9645ebfffd
Create Date: 2024-10-31 05:43:27.345285

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '744ed41773af'
down_revision = 'ff9645ebfffd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('is_admin',
               existing_type=sa.BOOLEAN(),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('is_admin',
               existing_type=sa.BOOLEAN(),
               nullable=True)

    # ### end Alembic commands ###