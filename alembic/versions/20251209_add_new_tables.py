"""Add ratings, favorites, genres, series_progress tables.

Revision ID: add_new_tables
Revises: 0fbe58431b10
Create Date: 2024-12-09

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ARRAY


# revision identifiers, used by Alembic.
revision: str = "add_new_tables"
down_revision: str | None = "0fbe58431b10"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # === ADD NEW COLUMNS TO MOVIES TABLE ===
    op.add_column("movies", sa.Column("poster_file_id", sa.String(255), nullable=True))
    op.add_column("movies", sa.Column("language", sa.String(10), server_default="uz", nullable=False))
    op.add_column("movies", sa.Column("country", sa.String(100), nullable=True))
    op.add_column("movies", sa.Column("average_rating", sa.Numeric(3, 2), server_default="0.00", nullable=False))
    op.add_column("movies", sa.Column("rating_count", sa.Integer(), server_default="0", nullable=False))

    # Add check constraint for rating
    op.create_check_constraint(
        "valid_rating",
        "movies",
        "average_rating >= 0 AND average_rating <= 5"
    )

    # === RATINGS TABLE ===
    op.create_table(
        "ratings",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("movie_id", UUID(as_uuid=True), sa.ForeignKey("movies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("review", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id", "movie_id", name="uq_user_movie_rating"),
        sa.CheckConstraint("score >= 1 AND score <= 5", name="valid_score"),
    )
    op.create_index("ix_ratings_user_id", "ratings", ["user_id"])
    op.create_index("ix_ratings_movie_id", "ratings", ["movie_id"])

    # === FAVORITES TABLE ===
    op.create_table(
        "favorites",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("movie_id", UUID(as_uuid=True), sa.ForeignKey("movies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id", "movie_id", name="uq_user_movie_favorite"),
    )
    op.create_index("ix_favorites_user_id", "favorites", ["user_id"])
    op.create_index("ix_favorites_movie_id", "favorites", ["movie_id"])

    # === GENRES TABLE ===
    op.create_table(
        "genres",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), unique=True, nullable=False),
        sa.Column("name_uz", sa.String(100), nullable=False),
        sa.Column("slug", sa.String(50), unique=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index("ix_genres_slug", "genres", ["slug"])

    # === MOVIE_GENRES JUNCTION TABLE ===
    op.create_table(
        "movie_genres",
        sa.Column("movie_id", UUID(as_uuid=True), sa.ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("genre_id", UUID(as_uuid=True), sa.ForeignKey("genres.id", ondelete="CASCADE"), primary_key=True),
    )
    op.create_index("ix_movie_genres_genre_id", "movie_genres", ["genre_id"])

    # === USER_SERIES_PROGRESS TABLE ===
    op.create_table(
        "user_series_progress",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("series_id", UUID(as_uuid=True), sa.ForeignKey("series.id", ondelete="CASCADE"), nullable=False),
        sa.Column("last_watched_part", sa.Integer(), server_default="1", nullable=False),
        sa.Column("completed_parts", ARRAY(sa.Integer()), server_default="{}", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id", "series_id", name="uq_user_series_progress"),
    )
    op.create_index("ix_user_series_progress_user_id", "user_series_progress", ["user_id"])
    op.create_index("ix_user_series_progress_series_id", "user_series_progress", ["series_id"])

    # === SEED DEFAULT GENRES ===
    op.execute("""
        INSERT INTO genres (id, name, name_uz, slug) VALUES
        (gen_random_uuid(), 'Action', 'Jangari', 'action'),
        (gen_random_uuid(), 'Comedy', 'Komediya', 'comedy'),
        (gen_random_uuid(), 'Drama', 'Drama', 'drama'),
        (gen_random_uuid(), 'Horror', 'Qo''rqinchli', 'horror'),
        (gen_random_uuid(), 'Romance', 'Romantik', 'romance'),
        (gen_random_uuid(), 'Sci-Fi', 'Fantastika', 'sci-fi'),
        (gen_random_uuid(), 'Thriller', 'Triller', 'thriller'),
        (gen_random_uuid(), 'Animation', 'Multfilm', 'animation'),
        (gen_random_uuid(), 'Documentary', 'Hujjatli', 'documentary'),
        (gen_random_uuid(), 'Family', 'Oilaviy', 'family')
    """)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table("user_series_progress")
    op.drop_table("movie_genres")
    op.drop_table("genres")
    op.drop_table("favorites")
    op.drop_table("ratings")

    # Drop new columns from movies
    op.drop_constraint("valid_rating", "movies", type_="check")
    op.drop_column("movies", "rating_count")
    op.drop_column("movies", "average_rating")
    op.drop_column("movies", "country")
    op.drop_column("movies", "language")
    op.drop_column("movies", "poster_file_id")
