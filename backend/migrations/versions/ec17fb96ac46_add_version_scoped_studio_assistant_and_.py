"""add version scoped studio assistant and revisions

Revision ID: ec17fb96ac46
Revises: 71bedf36b90f
Create Date: 2026-10-24 22:24:24.236912

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ec17fb96ac46'
down_revision = '71bedf36b90f'
branch_labels = None
depends_on = None


def upgrade():
    # Alter the existing plan table before creating tables that reference it. This keeps
    # SQLite batch recreation from affecting any existing assistant history.
    with op.batch_alter_table('project_ideas', schema=None) as batch_op:
        batch_op.add_column(sa.Column('parent_idea_id', sa.Uuid(), nullable=True))
        batch_op.create_foreign_key('fk_project_ideas_parent_idea_id', 'project_ideas', ['parent_idea_id'], ['id'], ondelete='SET NULL')

    op.create_table('studio_turns',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('idea_id', sa.Uuid(), nullable=False),
    sa.Column('author_id', sa.Uuid(), nullable=False),
    sa.Column('client_token', sa.String(length=36), nullable=False),
    sa.Column('mode', sa.String(length=10), nullable=False),
    sa.Column('prompt', sa.Text(), nullable=False),
    sa.Column('answer', sa.Text(), nullable=False),
    sa.Column('proposal', sa.JSON(), nullable=True),
    sa.Column('change_summary', sa.JSON(), nullable=False),
    sa.Column('model', sa.String(length=100), nullable=False),
    sa.Column('context_message_id', sa.Integer(), nullable=True),
    sa.Column('saved_idea_id', sa.Uuid(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['author_id'], ['profiles.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['idea_id'], ['project_ideas.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['saved_idea_id'], ['project_ideas.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('idea_id', 'author_id', 'client_token')
    )
    with op.batch_alter_table('studio_turns', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_studio_turns_idea_id'), ['idea_id'], unique=False)



def downgrade():
    with op.batch_alter_table('studio_turns', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_studio_turns_idea_id'))

    op.drop_table('studio_turns')
    with op.batch_alter_table('project_ideas', schema=None) as batch_op:
        batch_op.drop_constraint('fk_project_ideas_parent_idea_id', type_='foreignkey')
        batch_op.drop_column('parent_idea_id')
