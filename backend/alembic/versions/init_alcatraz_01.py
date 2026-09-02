"""migracion inicial tablas condominio

Revision ID: init_alcatraz_01
Revises: 
Create Date: 2026-09-01 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'init_alcatraz_01'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Usuarios
    op.create_table(
        'usuarios',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nombre', sa.String(length=100), nullable=False),
        sa.Column('apellido', sa.String(length=100), nullable=False),
        sa.Column('cedula', sa.String(length=20), nullable=False),
        sa.Column('telefono_whatsapp', sa.String(length=20), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('rol', sa.String(length=20), server_default='propietario', nullable=True),
        sa.Column('fecha_registro', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('cedula'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_usuarios_id'), 'usuarios', ['id'], unique=False)

    # 2. Apartamentos
    op.create_table(
        'apartamentos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('numero_apto', sa.String(length=10), nullable=False),
        sa.Column('piso', sa.String(length=5), nullable=True),
        sa.Column('torre', sa.String(length=20), server_default='Principal', nullable=True),
        sa.Column('alicuota', sa.Numeric(precision=5, scale=4), nullable=False),
        sa.Column('saldo_favor_usd', sa.Numeric(precision=10, scale=2), server_default='0.00', nullable=True),
        sa.Column('propietario_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['propietario_id'], ['usuarios.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_apartamentos_id'), 'apartamentos', ['id'], unique=False)

    # 3. Tasas BCV
    op.create_table(
        'tasas_bcv',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('fecha', sa.Date(), nullable=False),
        sa.Column('tasa_usd_ves', sa.Numeric(precision=12, scale=4), nullable=False),
        sa.Column('fecha_registro', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('fecha')
    )
    op.create_index(op.f('ix_tasas_bcv_fecha'), 'tasas_bcv', ['fecha'], unique=False)
    op.create_index(op.f('ix_tasas_bcv_id'), 'tasas_bcv', ['id'], unique=False)

    # 4. Recibos
    op.create_table(
        'recibos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('apartamento_id', sa.Integer(), nullable=False),
        sa.Column('mes_periodo', sa.String(length=7), nullable=False),
        sa.Column('monto_total_usd', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('monto_pendiente_usd', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('estado_pago', sa.String(length=20), server_default='pendiente', nullable=True),
        sa.Column('fecha_emision', sa.Date(), nullable=False),
        sa.Column('fecha_vencimiento', sa.Date(), nullable=False),
        sa.ForeignKeyConstraint(['apartamento_id'], ['apartamentos.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_recibos_id'), 'recibos', ['id'], unique=False)

    # 5. Pagos
    op.create_table(
        'pagos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('apartamento_id', sa.Integer(), nullable=False),
        sa.Column('recibo_id', sa.Integer(), nullable=False),
        sa.Column('metodo_pago', sa.String(length=30), nullable=False),
        sa.Column('banco_origen', sa.String(length=60), nullable=True),
        sa.Column('referencia_bancaria', sa.String(length=60), nullable=False),
        sa.Column('monto_declarado', sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column('moneda_pago', sa.String(length=5), nullable=False),
        sa.Column('tasa_bcv_aplicada', sa.Numeric(precision=12, scale=4), nullable=False),
        sa.Column('monto_equivalente_usd', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('comprobante_url', sa.String(length=500), nullable=False),
        sa.Column('estado_conciliacion', sa.String(length=20), server_default='en_revision', nullable=True),
        sa.Column('motivo_rechazo', sa.Text(), nullable=True),
        sa.Column('aprobado_por', sa.Integer(), nullable=True),
        sa.Column('fecha_reporte', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('fecha_aprobacion', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['apartamento_id'], ['apartamentos.id'], ),
        sa.ForeignKeyConstraint(['aprobado_por'], ['usuarios.id'], ),
        sa.ForeignKeyConstraint(['recibo_id'], ['recibos.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pagos_id'), 'pagos', ['id'], unique=False)


def downgrade() -> None:
    op.drop_table('pagos')
    op.drop_table('recibos')
    op.drop_table('tasas_bcv')
    op.drop_table('apartamentos')
    op.drop_table('usuarios')
