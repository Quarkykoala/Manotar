"""Add HRUser model

Revision ID: b3a525dc77ec
Revises: 680fbc3aac8b
Create Date: 2024-10-17 13:43:03.991736

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b3a525dc77ec'
down_revision = '680fbc3aac8b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('hr_user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=150), nullable=False),
    sa.Column('password_hash', sa.String(length=128), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('phone_number', sa.String(length=15), nullable=False),
    sa.Column('access_code', sa.String(length=8), nullable=False),
    sa.Column('is_authenticated', sa.Boolean(), nullable=True),
    sa.Column('conversation_started', sa.Boolean(), nullable=True),
    sa.Column('last_message_time', sa.DateTime(), nullable=True),
    sa.Column('message_count', sa.Integer(), nullable=True),
    sa.Column('conversation_history', sa.Text(), nullable=True),
    sa.Column('authentication_time', sa.DateTime(), nullable=True),
    sa.Column('consent_given', sa.Boolean(), nullable=True),
    sa.Column('location', sa.String(length=100), nullable=True),
    sa.Column('department', sa.String(length=100), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('phone_number')
    )
    op.create_table('keyword_stat',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('department', sa.String(length=100), nullable=False),
    sa.Column('location', sa.String(length=100), nullable=False),
    sa.Column('keyword', sa.String(length=100), nullable=False),
    sa.Column('count', sa.Integer(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('message',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('detected_keywords', sa.String(length=255), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('message')
    op.drop_table('keyword_stat')
    op.drop_table('user')
    op.drop_table('hr_user')
    # ### end Alembic commands ###
