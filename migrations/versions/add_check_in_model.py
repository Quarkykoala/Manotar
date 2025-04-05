"""add check in model

Revision ID: check_in_model_20240525
Revises: employee_model_20240404
Create Date: 2024-05-25 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'check_in_model_20240525'
down_revision = 'employee_model_20240404'
branch_labels = None
depends_on = None


def upgrade():
    # Create check_in table
    op.create_table(
        'check_in',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('employee_id', sa.Integer(), nullable=True),
        
        # Check-in state
        sa.Column('state', sa.String(length=50), nullable=True),
        sa.Column('is_completed', sa.Boolean(), nullable=True),
        
        # Check-in responses
        sa.Column('mood_score', sa.Integer(), nullable=True),
        sa.Column('mood_description', sa.Text(), nullable=True),
        sa.Column('stress_level', sa.Integer(), nullable=True),
        sa.Column('stress_factors', sa.Text(), nullable=True),
        sa.Column('qualitative_feedback', sa.Text(), nullable=True),
        
        # System-generated analysis
        sa.Column('sentiment_score', sa.Float(), nullable=True),
        sa.Column('recommendations', sa.Text(), nullable=True),
        sa.Column('follow_up_required', sa.Boolean(), nullable=True),
        sa.Column('follow_up_notes', sa.Text(), nullable=True),
        
        # Timeout tracking
        sa.Column('last_interaction_time', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('is_expired', sa.Boolean(), nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        
        # Constraints
        sa.ForeignKeyConstraint(['employee_id'], ['employee.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add indexes for better query performance
    op.create_index(op.f('ix_check_in_employee_id'), 'check_in', ['employee_id'], unique=False)
    op.create_index(op.f('ix_check_in_user_id'), 'check_in', ['user_id'], unique=False)
    op.create_index(op.f('ix_check_in_created_at'), 'check_in', ['created_at'], unique=False)
    op.create_index(op.f('ix_check_in_state'), 'check_in', ['state'], unique=False)


def downgrade():
    # Drop indexes first
    op.drop_index(op.f('ix_check_in_state'), table_name='check_in')
    op.drop_index(op.f('ix_check_in_created_at'), table_name='check_in')
    op.drop_index(op.f('ix_check_in_user_id'), table_name='check_in')
    op.drop_index(op.f('ix_check_in_employee_id'), table_name='check_in')
    
    # Then drop the table
    op.drop_table('check_in') 