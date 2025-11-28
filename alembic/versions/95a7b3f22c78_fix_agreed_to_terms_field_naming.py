"""Fix agreed_to_terms field naming

Revision ID: 95a7b3f22c78
Revises: 
Create Date: 2025-11-26 15:26:44.766044

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '95a7b3f22c78'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('users',
                  sa.Column('agreed_to_terms',
                            sa.Boolean(),
                            nullable=False,
                            server_default=sa.text('false'))
                  )

    op.add_column('users',
                  sa.Column('send_marketing_emails',
                            sa.Boolean(),
                            nullable=False,
                            server_default=sa.text('false'))
                  )


def downgrade():
    op.drop_column('users', 'send_marketing_emails')
    op.drop_column('users', 'agreed_to_terms')
