"""convert fields to json

Revision ID: c0523f1f6d99
Revises:
Create Date: 2026-08-16
"""

from typing import Sequence, Union
import json

from alembic import op
import sqlalchemy as sa


revision: str = "c0523f1f6d99"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def string_to_list(value):
    """
    Convert old comma-separated/string data into a Python list.
    """
    if value is None:
        return []

    value = str(value).strip()

    if not value:
        return []

    # If the old value is already valid JSON list
    try:
        parsed = json.loads(value)
        if isinstance(parsed, list):
            return parsed
    except (json.JSONDecodeError, TypeError):
        pass

    # Convert comma-separated text to list
    return [
        item.strip()
        for item in value.split(",")
        if item.strip()
    ]


def upgrade() -> None:

    connection = op.get_bind()

    # ---------------------------------------------------------
    # 1. Convert old AnalysisResume.skills data to JSON strings
    # ---------------------------------------------------------

    rows = connection.execute(
        sa.text(
            "SELECT id, skills FROM analysis_resumes"
        )
    ).fetchall()

    for row in rows:
        skills_list = string_to_list(row.skills)

        connection.execute(
            sa.text(
                """
                UPDATE analysis_resumes
                SET skills = :skills
                WHERE id = :id
                """
            ),
            {
                "skills": json.dumps(skills_list),
                "id": row.id,
            },
        )

    # ---------------------------------------------------------
    # 2. Convert CareerAdvisor fields
    # ---------------------------------------------------------

    career_columns = [
        "missing_skills",
        "courses",
        "certifications",
        "learning_resources",
        "career_questions",
    ]

    for column in career_columns:

        rows = connection.execute(
            sa.text(
                f"SELECT id, {column} FROM career_advisors"
            )
        ).fetchall()

        for row in rows:

            values = string_to_list(getattr(row, column))

            connection.execute(
                sa.text(
                    f"""
                    UPDATE career_advisors
                    SET {column} = :value
                    WHERE id = :id
                    """
                ),
                {
                    "value": json.dumps(values),
                    "id": row.id,
                },
            )

    # ---------------------------------------------------------
    # 3. Change existing columns to JSON
    # ---------------------------------------------------------

    with op.batch_alter_table(
        "analysis_resumes",
        recreate="always"
    ) as batch_op:

        batch_op.alter_column(
            "skills",
            existing_type=sa.VARCHAR(),
            type_=sa.JSON(),
            existing_nullable=False,
        )

    with op.batch_alter_table(
        "career_advisors",
        recreate="always"
    ) as batch_op:

        for column in career_columns:
            batch_op.alter_column(
                column,
                existing_type=sa.VARCHAR(),
                type_=sa.JSON(),
                existing_nullable=False,
            )

    # ---------------------------------------------------------
    # 4. Add new Job column
    # ---------------------------------------------------------

    with op.batch_alter_table(
        "jobs",
        recreate="always"
    ) as batch_op:

        batch_op.add_column(
            sa.Column(
                "required_skills",
                sa.JSON(),
                nullable=True,
            )
        )

    # Existing jobs get an empty list
    connection.execute(
        sa.text(
            """
            UPDATE jobs
            SET required_skills = :value
            WHERE required_skills IS NULL
            """
        ),
        {
            "value": json.dumps([])
        },
    )

    with op.batch_alter_table(
        "jobs",
        recreate="always"
    ) as batch_op:

        batch_op.alter_column(
            "required_skills",
            existing_type=sa.JSON(),
            nullable=False,
        )

    # ---------------------------------------------------------
    # 5. Add Recommendation list columns
    # ---------------------------------------------------------

    with op.batch_alter_table(
        "recommendations",
        recreate="always"
    ) as batch_op:

        batch_op.add_column(
            sa.Column(
                "matched_skills",
                sa.JSON(),
                nullable=True,
            )
        )

        batch_op.add_column(
            sa.Column(
                "missing_skills",
                sa.JSON(),
                nullable=True,
            )
        )

    # Existing recommendations get empty lists
    connection.execute(
        sa.text(
            """
            UPDATE recommendations
            SET matched_skills = :value
            WHERE matched_skills IS NULL
            """
        ),
        {
            "value": json.dumps([])
        },
    )

    connection.execute(
        sa.text(
            """
            UPDATE recommendations
            SET missing_skills = :value
            WHERE missing_skills IS NULL
            """
        ),
        {
            "value": json.dumps([])
        },
    )

    with op.batch_alter_table(
        "recommendations",
        recreate="always"
    ) as batch_op:

        batch_op.alter_column(
            "matched_skills",
            existing_type=sa.JSON(),
            nullable=False,
        )

        batch_op.alter_column(
            "missing_skills",
            existing_type=sa.JSON(),
            nullable=False,
        )


def downgrade() -> None:

    connection = op.get_bind()

    # ---------------------------------------------------------
    # Convert JSON lists back to comma-separated strings
    # ---------------------------------------------------------

    rows = connection.execute(
        sa.text(
            "SELECT id, skills FROM analysis_resumes"
        )
    ).fetchall()

    for row in rows:

        try:
            values = json.loads(row.skills)
            text_value = ", ".join(values)
        except Exception:
            text_value = str(row.skills)

        connection.execute(
            sa.text(
                """
                UPDATE analysis_resumes
                SET skills = :value
                WHERE id = :id
                """
            ),
            {
                "value": text_value,
                "id": row.id,
            },
        )

    career_columns = [
        "missing_skills",
        "courses",
        "certifications",
        "learning_resources",
        "career_questions",
    ]

    for column in career_columns:

        rows = connection.execute(
            sa.text(
                f"SELECT id, {column} FROM career_advisors"
            )
        ).fetchall()

        for row in rows:

            try:
                values = json.loads(getattr(row, column))
                text_value = ", ".join(values)
            except Exception:
                text_value = str(getattr(row, column))

            connection.execute(
                sa.text(
                    f"""
                    UPDATE career_advisors
                    SET {column} = :value
                    WHERE id = :id
                    """
                ),
                {
                    "value": text_value,
                    "id": row.id,
                },
            )

    # ---------------------------------------------------------
    # JSON -> VARCHAR
    # ---------------------------------------------------------

    with op.batch_alter_table(
        "analysis_resumes",
        recreate="always"
    ) as batch_op:

        batch_op.alter_column(
            "skills",
            existing_type=sa.JSON(),
            type_=sa.VARCHAR(),
            existing_nullable=False,
        )

    with op.batch_alter_table(
        "career_advisors",
        recreate="always"
    ) as batch_op:

        for column in career_columns:
            batch_op.alter_column(
                column,
                existing_type=sa.JSON(),
                type_=sa.VARCHAR(),
                existing_nullable=False,
            )

    # ---------------------------------------------------------
    # Remove recommendation columns
    # ---------------------------------------------------------

    with op.batch_alter_table(
        "recommendations",
        recreate="always"
    ) as batch_op:

        batch_op.drop_column("missing_skills")
        batch_op.drop_column("matched_skills")

    # ---------------------------------------------------------
    # Remove job column
    # ---------------------------------------------------------

    with op.batch_alter_table(
        "jobs",
        recreate="always"
    ) as batch_op:

        batch_op.drop_column("required_skills")