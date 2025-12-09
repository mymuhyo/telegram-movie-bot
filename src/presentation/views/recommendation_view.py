"""Recommendation view for formatting recommendation messages."""

from src.application.dto import MovieDTO


class RecommendationView:
    """Formats recommendation data for display in Telegram."""

    @staticmethod
    def format_recommendations_header() -> str:
        """Format recommendations header."""
        return "🎯 *Sizga tavsiya*\n\nSizning didingizga mos kinolar:"

    @staticmethod
    def format_similar_movies_header(movie_title: str) -> str:
        """
        Format similar movies header.

        Args:
            movie_title: Title of the reference movie

        Returns:
            Formatted header
        """
        escaped = RecommendationView._escape_md(movie_title)
        return f"🎬 *O'xshash kinolar*\n\n*{escaped}* ga o'xshash:"

    @staticmethod
    def format_continue_watching_header() -> str:
        """Format continue watching header."""
        return "▶️ *Davom etish*\n\nSiz ko'rayotgan seriallar:"

    @staticmethod
    def format_popular_header() -> str:
        """Format popular movies header."""
        return "🔥 *Mashhur kinolar*\n\nEng ko'p yuklangan kinolar:"

    @staticmethod
    def format_top_rated_header() -> str:
        """Format top rated movies header."""
        return "⭐ *Eng yaxshilari*\n\nEng yuqori baholangan kinolar:"

    @staticmethod
    def format_recent_header() -> str:
        """Format recent movies header."""
        return "🆕 *Yangi kinolar*\n\nYaqinda qo'shilgan kinolar:"

    @staticmethod
    def format_empty_recommendations() -> str:
        """Format message when no recommendations available."""
        lines = [
            "📭 *Tavsiyalar uchun ma'lumot yetarli emas*",
            "",
            "Botdan ko'proq foydalaning:",
            "• Kinolarni ko'ring",
            "• Baholang ⭐",
            "• Sevimlilarga qo'shing ❤️",
            "",
            "Shunda sizga mos tavsiyalar chiqadi!",
        ]
        return "\n".join(lines)

    @staticmethod
    def format_recommendation_item(movie: MovieDTO, index: int) -> str:
        """
        Format single recommendation item.

        Args:
            movie: Movie DTO
            index: Item index (1-based)

        Returns:
            Formatted item string
        """
        title = RecommendationView._escape_md(movie.title[:40])
        if len(movie.title) > 40:
            title += "\\.\\.\\."

        parts = [f"{index}\\. `{movie.code}` \\- {title}"]

        details = []
        if movie.year:
            details.append(f"{movie.year}")
        if movie.rating_count > 0:
            details.append(f"⭐{movie.average_rating:.1f}")
        if movie.download_count > 0:
            details.append(f"📥{movie.download_count}")

        if details:
            parts.append(f"   _{'  '.join(details)}_")

        return "\n".join(parts)

    @staticmethod
    def format_recommendation_list(movies: list[MovieDTO]) -> str:
        """
        Format full recommendation list.

        Args:
            movies: List of recommended movies

        Returns:
            Formatted list with header
        """
        if not movies:
            return RecommendationView.format_empty_recommendations()

        lines = [RecommendationView.format_recommendations_header(), ""]

        for i, movie in enumerate(movies, 1):
            lines.append(RecommendationView.format_recommendation_item(movie, i))
            lines.append("")

        lines.append("⬇️ Tanlang yoki kodni yuboring:")

        return "\n".join(lines)

    @staticmethod
    def format_similar_list(movies: list[MovieDTO], reference_title: str) -> str:
        """
        Format similar movies list.

        Args:
            movies: List of similar movies
            reference_title: Title of the reference movie

        Returns:
            Formatted list with header
        """
        if not movies:
            return f"❌ *{RecommendationView._escape_md(reference_title)}* ga o'xshash kinolar topilmadi"

        lines = [RecommendationView.format_similar_movies_header(reference_title), ""]

        for i, movie in enumerate(movies, 1):
            lines.append(RecommendationView.format_recommendation_item(movie, i))
            lines.append("")

        return "\n".join(lines)

    @staticmethod
    def format_why_recommended(movie: MovieDTO) -> str:
        """
        Format explanation for why movie is recommended.

        Args:
            movie: Recommended movie

        Returns:
            Explanation string
        """
        reasons = []

        if movie.rating_count > 0 and movie.average_rating >= 4.0:
            reasons.append("⭐ Yuqori reyting")

        if movie.download_count > 100:
            reasons.append("🔥 Mashhur")

        if movie.year and movie.year >= 2023:
            reasons.append("🆕 Yangi")

        if movie.is_series:
            reasons.append("📺 Serial")

        if reasons:
            return f"💡 Nima uchun: {', '.join(reasons)}"
        return ""

    @staticmethod
    def _escape_md(text: str) -> str:
        """Escape MarkdownV2 special characters."""
        chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        for char in chars:
            text = text.replace(char, f"\\{char}")
        return text
