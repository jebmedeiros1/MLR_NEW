from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'tags',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=1024), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_tags_id'), 'tags', ['id'], unique=False)

    op.create_table(
        'detection_runs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('model_name', sa.String(length=255), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('parameters', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_detection_runs_id'), 'detection_runs', ['id'], unique=False)

    op.create_table(
        'anomaly_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.Column('run_id', sa.Integer(), nullable=False),
        sa.Column('detected_at', sa.DateTime(), nullable=False),
        sa.Column('severity', sa.Float(), nullable=False),
        sa.Column('message', sa.String(length=1024), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['run_id'], ['detection_runs.id'], ),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_anomaly_events_id'), 'anomaly_events', ['id'], unique=False)
    op.create_index(op.f('ix_anomaly_events_run_id'), 'anomaly_events', ['run_id'], unique=False)
    op.create_index(op.f('ix_anomaly_events_tag_id'), 'anomaly_events', ['tag_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_anomaly_events_tag_id'), table_name='anomaly_events')
    op.drop_index(op.f('ix_anomaly_events_run_id'), table_name='anomaly_events')
    op.drop_index(op.f('ix_anomaly_events_id'), table_name='anomaly_events')
    op.drop_table('anomaly_events')
    op.drop_index(op.f('ix_detection_runs_id'), table_name='detection_runs')
    op.drop_table('detection_runs')
    op.drop_index(op.f('ix_tags_id'), table_name='tags')
    op.drop_table('tags')
