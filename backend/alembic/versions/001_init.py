"""init - create all tables

Revision ID: 001
Revises:
Create Date: 2026-04-01

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import Integer, String, Text, ForeignKey, Enum as SQLEnum, Numeric, JSON, Date
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum types
    op.execute("CREATE TABLE IF NOT EXISTS strategy_mode (name VARCHAR(20), PRIMARY KEY (name))")
    op.execute("INSERT INTO strategy_mode (name) VALUES ('backtest'), ('paper'), ('live') ON DUPLICATE KEY UPDATE name=name")

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', Integer, primary_key=True, autoincrement=True),
        sa.Column('username', String(64), nullable=False, unique=True),
        sa.Column('password_hash', String(256), nullable=False),
        sa.Column('qmt_user', String(64), nullable=True),
        sa.Column('qmt_password', String(256), nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    # Create strategies table
    op.create_table(
        'strategies',
        sa.Column('id', Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
        sa.Column('name', String(128), nullable=False),
        sa.Column('description', Text, nullable=True),
        sa.Column('code', Text, nullable=False),
        sa.Column('mode', SQLEnum('backtest', 'paper', 'live', name='strategy_mode'), nullable=False),
        sa.Column('config', JSON, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    # Create backtests table
    op.create_table(
        'backtests',
        sa.Column('id', Integer, primary_key=True, autoincrement=True),
        sa.Column('strategy_id', Integer, ForeignKey('strategies.id'), nullable=False),
        sa.Column('start_date', Date, nullable=False),
        sa.Column('end_date', Date, nullable=False),
        sa.Column('initial_cash', Numeric(16, 2), server_default='1000000', nullable=False),
        sa.Column('result_json', JSON, nullable=True),
        sa.Column('status', SQLEnum('pending', 'running', 'completed', 'failed', name='backtest_status'), nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    # Create orders table
    op.create_table(
        'orders',
        sa.Column('id', Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
        sa.Column('backtest_id', Integer, ForeignKey('backtests.id'), nullable=True),
        sa.Column('symbol', String(16), nullable=False),
        sa.Column('direction', SQLEnum('buy', 'sell', name='order_direction'), nullable=False),
        sa.Column('order_type', SQLEnum('market', 'limit', name='order_type'), nullable=False),
        sa.Column('price', Numeric(10, 2), nullable=True),
        sa.Column('volume', Integer, nullable=False),
        sa.Column('filled_volume', Integer, server_default='0', nullable=False),
        sa.Column('status', SQLEnum('pending', 'submitted', 'filled', 'cancelled', 'rejected', name='order_status'), nullable=False),
        sa.Column('mode', SQLEnum('backtest', 'paper', 'live', name='order_mode'), nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    # Create positions table
    op.create_table(
        'positions',
        sa.Column('id', Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
        sa.Column('symbol', String(16), nullable=False),
        sa.Column('volume', Integer, server_default='0', nullable=False),
        sa.Column('avg_cost', Numeric(10, 2), server_default='0', nullable=False),
        sa.Column('current_price', Numeric(10, 2), nullable=True),
        sa.Column('frozen_volume', Integer, server_default='0', nullable=False),
        sa.Column('mode', SQLEnum('backtest', 'paper', 'live', name='position_mode'), nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.UniqueConstraint('user_id', 'symbol', 'mode', name='uq_user_symbol_mode'),
    )


def downgrade() -> None:
    op.drop_table('positions')
    op.drop_table('orders')
    op.drop_table('backtests')
    op.drop_table('strategies')
    op.drop_table('users')
    op.execute("DROP TABLE IF EXISTS strategy_mode")
