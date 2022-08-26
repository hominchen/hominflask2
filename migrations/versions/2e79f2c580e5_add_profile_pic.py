"""add profile pic

Revision ID: 2e79f2c580e5
Revises: 95db0e3327d2
Create Date: 2022-08-26 15:29:38.461298

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2e79f2c580e5'
down_revision = '95db0e3327d2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(None, 'posts', 'users', ['poster_id'], ['id'])
    op.drop_column('posts', 'author')
    op.add_column('users', sa.Column('profile_pic', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'profile_pic')
    op.add_column('posts', sa.Column('author', sa.VARCHAR(length=255), nullable=True))
    op.drop_constraint(None, 'posts', type_='foreignkey')
    # ### end Alembic commands ###
