"""Initial schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2025-01-19

Creates initial database schema:
- buildings: таблица зданий с координатами
- activities: таблица деятельностей (иерархическая, до 3 уровней)
- organizations: таблица организаций
- organization_activities: связующая таблица M2M
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Таблица зданий
    op.create_table(
        'buildings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('address', sa.String(length=500), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_buildings_id', 'buildings', ['id'], unique=False)
    op.create_index('ix_buildings_address', 'buildings', ['address'], unique=False)
    op.create_index('idx_building_coordinates', 'buildings', ['latitude', 'longitude'], unique=False)

    # Таблица деятельностей
    op.create_table(
        'activities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('level', sa.Integer(), nullable=False, server_default='1'),
        sa.CheckConstraint('level >= 1 AND level <= 3', name='check_activity_level'),
        sa.ForeignKeyConstraint(['parent_id'], ['activities.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_activities_id', 'activities', ['id'], unique=False)
    op.create_index('ix_activities_name', 'activities', ['name'], unique=False)
    op.create_index('idx_activity_parent', 'activities', ['parent_id'], unique=False)

    # Таблица организаций
    op.create_table(
        'organizations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=500), nullable=False),
        sa.Column('phone_numbers', postgresql.ARRAY(sa.String(length=50)), nullable=False),
        sa.Column('building_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['building_id'], ['buildings.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_organizations_id', 'organizations', ['id'], unique=False)
    op.create_index('ix_organizations_name', 'organizations', ['name'], unique=False)
    op.create_index('idx_organization_building', 'organizations', ['building_id'], unique=False)
    op.create_index('idx_organization_name_lower', 'organizations', ['name'], unique=False)

    # Связующая таблица M2M
    op.create_table(
        'organization_activities',
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('activity_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['activity_id'], ['activities.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('organization_id', 'activity_id')
    )


def downgrade() -> None:
    op.drop_table('organization_activities')
    op.drop_index('idx_organization_name_lower', table_name='organizations')
    op.drop_index('idx_organization_building', table_name='organizations')
    op.drop_index('ix_organizations_name', table_name='organizations')
    op.drop_index('ix_organizations_id', table_name='organizations')
    op.drop_table('organizations')
    op.drop_index('idx_activity_parent', table_name='activities')
    op.drop_index('ix_activities_name', table_name='activities')
    op.drop_index('ix_activities_id', table_name='activities')
    op.drop_table('activities')
    op.drop_index('idx_building_coordinates', table_name='buildings')
    op.drop_index('ix_buildings_address', table_name='buildings')
    op.drop_index('ix_buildings_id', table_name='buildings')
    op.drop_table('buildings')
