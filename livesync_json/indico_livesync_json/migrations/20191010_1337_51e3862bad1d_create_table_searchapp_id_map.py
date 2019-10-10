"""Create table searchapp_id_map

Revision ID: 51e3862bad1d
Revises:
Create Date: 2019-10-10 13:37:57.440636
"""

import sqlalchemy as sa
from alembic import op

from sqlalchemy.sql.ddl import CreateSchema, DropSchema
from indico.core.db.sqlalchemy import PyIntEnum, UTCDateTime

from indico_livesync_json.models.search_id_map import EntryType

# revision identifiers, used by Alembic.
revision = '51e3862bad1d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute(CreateSchema('plugin_livesync_json'))
    op.create_table('searchapp_id_map',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('search_id', sa.Integer(), nullable=False),
                    sa.Column('timestamp', UTCDateTime, nullable=False),
                    sa.Column('entry_type', PyIntEnum(EntryType), nullable=False),
                    sa.Column('event_id', sa.Integer(), nullable=True),
                    sa.Column('contrib_id', sa.Integer(), nullable=True),
                    sa.Column('subcontrib_id', sa.Integer(), nullable=True),
                    sa.Column('attachment_id', sa.Integer(), nullable=True),
                    sa.Column('note_id', sa.Integer(), nullable=True),
                    sa.Column('subcontrib_id', sa.Integer(), nullable=True),
                    sa.PrimaryKeyConstraint('id'),
                    schema='plugin_livesync_json')


def downgrade():
    op.drop_table('searchapp_id_map', schema='plugin_livesync_json')
    op.execute(DropSchema('plugin_livesync_json'))
