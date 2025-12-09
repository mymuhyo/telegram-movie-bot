"""Movie view for formatting movie cards and messages."""

from src.application.dto import MovieCardDTO, MovieDTO


class MovieView:
    """Formats movie data for display in Telegram."""

    @staticmethod
    def format_movie_card(movie: MovieDTO, show_rating: bool = True) -> str:
        """
        Format movie card for display.

        Args:
            movie: Movie DTO
            show_rating: Whether to show rating

        Returns:
            Formatted message text
        """
        lines = [f"🎬 *{MovieView._escape_md(movie.title)}*", ""]

        # Code
        lines.append(f"🔢 Kod: `{movie.code}`")

        # Year
        if movie.year:
            lines.append(f"📅 Yil: {movie.year}")

        # Duration
        if movie.duration_minutes:
            hours = movie.duration_minutes // 60
            mins = movie.duration_minutes % 60
            if hours > 0:
                lines.append(f"⏱ Davomiyligi: {hours}s {mins}d")
            else:
                lines.append(f"⏱ Davomiyligi: {mins} daqiqa")

        # Quality
        lines.append(f"📺 Sifat: {movie.quality}")

        # Rating
        if show_rating:
            lines.append(f"⭐ Reyting: {movie.rating_display}")

        # Downloads
        lines.append(f"📥 Yuklanishlar: {movie.download_count} ta")

        # Series info
        if movie.is_series:
            lines.append("")
            lines.append(f"📺 Serial: {movie.series_name}")
            if movie.part_number and movie.total_parts:
                lines.append(f"📂 Qism: {movie.part_number}/{movie.total_parts}")

        # Description
        if movie.description:
            lines.append("")
            desc = movie.description[:200]
            if len(movie.description) > 200:
                desc += "..."
            lines.append(f"📝 {MovieView._escape_md(desc)}")

        return "\n".join(lines)

    @staticmethod
    def format_movie_card_full(card: MovieCardDTO) -> str:
        """
        Format full movie card with user-specific data.

        Args:
            card: Movie card DTO with user data

        Returns:
            Formatted message text
        """
        lines = [f"🎬 *{MovieView._escape_md(card.movie.title)}*", ""]

        # Code
        lines.append(f"🔢 Kod: `{card.movie.code}`")

        # Year
        if card.movie.year:
            lines.append(f"📅 Yil: {card.movie.year}")

        # Duration
        if card.movie.duration_minutes:
            hours = card.movie.duration_minutes // 60
            mins = card.movie.duration_minutes % 60
            if hours > 0:
                lines.append(f"⏱ Davomiyligi: {hours}s {mins}d")
            else:
                lines.append(f"⏱ Davomiyligi: {mins} daqiqa")

        # Quality
        lines.append(f"📺 Sifat: {card.movie.quality}")

        # Rating with user's rating
        avg_rating = card.movie.rating_display
        if card.user_rating:
            user_stars = "⭐" * card.user_rating
            lines.append(f"⭐ Reyting: {avg_rating}")
            lines.append(f"👤 Sizning bahongiz: {user_stars}")
        else:
            lines.append(f"⭐ Reyting: {avg_rating}")
            lines.append("👤 Siz hali baholamadingiz")

        # Favorite status
        if card.is_favorite:
            lines.append("❤️ Sevimlilar ro'yxatida")

        # Downloads
        lines.append(f"📥 Yuklanishlar: {card.movie.download_count} ta")

        # Series info
        if card.movie.is_series:
            lines.append("")
            lines.append(f"📺 Serial: {card.movie.series_name}")
            if card.movie.part_number and card.movie.total_parts:
                lines.append(f"📂 Qism: {card.movie.part_number}/{card.movie.total_parts}")

        return "\n".join(lines)

    @staticmethod
    def format_caption(movie: MovieDTO) -> str:
        """
        Format short caption for video.

        Args:
            movie: Movie DTO

        Returns:
            Short caption
        """
        parts = [f"🎬 {movie.title}", f"🔢 Kod: {movie.code}"]

        if movie.rating_count > 0:
            parts.append(f"⭐ {movie.average_rating}")

        if movie.is_series and movie.part_number:
            parts.append(f"📺 {movie.part_number}-qism")

        return " | ".join(parts)

    @staticmethod
    def format_rating_prompt(movie: MovieDTO, current_rating: int | None = None) -> str:
        """
        Format rating prompt message.

        Args:
            movie: Movie DTO
            current_rating: User's current rating if any

        Returns:
            Rating prompt message
        """
        lines = [f"⭐ *{MovieView._escape_md(movie.title)}* ni baholang", ""]

        if current_rating:
            stars = "⭐" * current_rating
            lines.append(f"Hozirgi bahongiz: {stars}")
            lines.append("")

        lines.append("1-5 orasida tanlang:")

        return "\n".join(lines)

    @staticmethod
    def format_rating_success(movie: MovieDTO, score: int) -> str:
        """
        Format rating success message.

        Args:
            movie: Movie DTO
            score: New rating score

        Returns:
            Success message
        """
        stars = "⭐" * score
        return f"✅ Rahmat! *{MovieView._escape_md(movie.title)}* uchun bahongiz: {stars}"

    @staticmethod
    def format_search_result(movies: list[MovieDTO], query: str) -> str:
        """
        Format search results.

        Args:
            movies: List of found movies
            query: Search query

        Returns:
            Formatted search results
        """
        if not movies:
            return f"❌ '{query}' bo'yicha hech narsa topilmadi"

        lines = [f"🔍 *Natijalar:* {query}", ""]

        for i, movie in enumerate(movies[:10], 1):
            rating = ""
            if movie.rating_count > 0:
                rating = f" ⭐{movie.average_rating}"

            title = MovieView._escape_md(movie.title[:40])
            if len(movie.title) > 40:
                title += "..."

            lines.append(f"{i}. `{movie.code}` — {title}{rating}")

        if len(movies) > 10:
            lines.append(f"\n...va yana {len(movies) - 10} ta")

        return "\n".join(lines)

    @staticmethod
    def _escape_md(text: str) -> str:
        """Escape markdown special characters."""
        chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        for char in chars:
            text = text.replace(char, f"\\{char}")
        return text
