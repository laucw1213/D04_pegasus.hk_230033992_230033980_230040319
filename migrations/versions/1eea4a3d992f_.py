"""empty message

Revision ID: 1eea4a3d992f
Revises: 8bc75bf5af26
Create Date: 2024-04-16 02:42:12.498581

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1eea4a3d992f'
down_revision = '8bc75bf5af26'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('product1',
    sa.Column('id1', sa.Integer(), nullable=False),
    sa.Column('name1', sa.String(length=64), nullable=True),
    sa.Column('price1', sa.Float(), nullable=True),
    sa.Column('cart_id1', sa.Integer(), nullable=True),
    sa.Column('category_id1', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['cart_id1'], ['cart.id'], ),
    sa.ForeignKeyConstraint(['category_id1'], ['category.id'], ),
    sa.PrimaryKeyConstraint('id1')
    )
    with op.batch_alter_table('product1', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_product1_name1'), ['name1'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product1', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_product1_name1'))

    op.drop_table('product1')
    # ### end Alembic commands ###
