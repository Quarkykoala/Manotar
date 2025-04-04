"""Update models for API v1

Revision ID: update_models_for_api_v1
Create Date: 2023-04-06 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'update_models_for_api_v1'
down_revision = '65929569b49a'  # Set to match your last migration
branch_labels = None
depends_on = None


def upgrade():
    # Add new fields to the User table
    op.add_column('user', sa.Column('conversation_started', sa.Boolean(), nullable=True))
    op.add_column('user', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('user', sa.Column('updated_at', sa.DateTime(), nullable=True))
    
    # Add new fields to the Message table
    op.add_column('message', sa.Column('is_from_user', sa.Boolean(), nullable=True))
    op.add_column('message', sa.Column('sentiment_score', sa.Float(), nullable=True))
    op.add_column('message', sa.Column('department', sa.String(length=50), nullable=True))
    op.add_column('message', sa.Column('location', sa.String(length=50), nullable=True))
    
    # Add new fields to the KeywordStat table
    op.add_column('keyword_stat', sa.Column('department', sa.String(length=50), nullable=True))
    op.add_column('keyword_stat', sa.Column('location', sa.String(length=50), nullable=True))
    
    # Create SentimentLog table
    op.create_table('sentiment_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('department', sa.String(length=50), nullable=True),
        sa.Column('location', sa.String(length=50), nullable=True),
        sa.Column('sentiment_score', sa.Float(), nullable=False),
        sa.Column('message_id', sa.Integer(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['message_id'], ['message.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create AuthUser table
    op.create_table('auth_user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('password_hash', sa.String(length=200), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    
    # Create AuditLog table
    op.create_table('audit_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('target', sa.String(length=100), nullable=True),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(length=50), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['auth_user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    # Drop new tables
    op.drop_table('audit_log')
    op.drop_table('auth_user')
    op.drop_table('sentiment_log')
    
    # Drop new columns from KeywordStat
    op.drop_column('keyword_stat', 'location')
    op.drop_column('keyword_stat', 'department')
    
    # Drop new columns from Message
    op.drop_column('message', 'location')
    op.drop_column('message', 'department')
    op.drop_column('message', 'sentiment_score')
    op.drop_column('message', 'is_from_user')
    
    # Drop new columns from User
    op.drop_column('user', 'updated_at')
    op.drop_column('user', 'created_at')
    op.drop_column('user', 'conversation_started') 