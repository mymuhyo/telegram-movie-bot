"""Search view for formatting search-related messages."""

from src.application.dto import MovieDTO, SearchFilters, SearchResult


class SearchView:
    """Formats search data for display in Telegram."""

    @staticmethod
    def format_search_results(result: SearchResult) -> str:
        """
        Format search results.

        Args:
            result: Search result container

        Returns:
            Formatted message
        """
        if not result.movies:
            return SearchView.format_no_results(result.query, result.filters)

        lines = [f"🔍 *Natijalar:* {SearchView._escape_md(result.query)}"]

        # Show applied filters
        if result.filters.has_filters:
            filters_text = SearchView._format_applied_filters(result.filters)
            lines.append(f"🔧 {filters_text}")

        lines.append("")
        lines.append(f"📊 Topildi: {result.total} ta kino")
        lines.append("")

        # Movie list
        for i, movie in enumerate(result.movies, start=(result.page - 1) * result.per_page + 1):
            lines.append(SearchView._format_movie_item(movie, i))

        # Pagination info
        if result.total_pages > 1:
            lines.append("")
            lines.append(f"📄 Sahifa: {result.page}/{result.total_pages}")

        lines.append("")
        lines.append("⬇️ Tanlang yoki kodni yuboring:")

        return "\n".join(lines)

    @staticmethod
    def format_no_results(query: str, filters: SearchFilters) -> str:
        """
        Format no results message.

        Args:
            query: Search query
            filters: Applied filters

        Returns:
            Formatted message
        """
        lines = [
            f"❌ *Topilmadi:* {SearchView._escape_md(query)}",
            "",
        ]

        if filters.has_filters:
            lines.append("🔧 Qo'llangan filtrlar:")
            lines.append(SearchView._format_applied_filters(filters))
            lines.append("")
            lines.append("💡 Filtrlarni o'zgartiring yoki tozalang")
        else:
            lines.extend([
                "💡 *Tavsiyalar:*",
                "• Boshqa kalit so'zlar bilan qidiring",
                "• Filtrlar bilan qidiring",
                "• Kino nomini aniq yozing",
            ])

        return "\n".join(lines)

    @staticmethod
    def format_filters_menu(filters: SearchFilters) -> str:
        """
        Format filters selection menu.

        Args:
            filters: Current filters

        Returns:
            Formatted message
        """
        lines = [
            "🔧 *Qidiruv filtrlari*",
            "",
            "Quyidagi filtrlarni tanlang:",
        ]

        if filters.has_filters:
            lines.append("")
            lines.append("*Joriy filtrlar:*")
            lines.append(SearchView._format_applied_filters(filters))

        return "\n".join(lines)

    @staticmethod
    def format_year_filter() -> str:
        """Format year filter selection message."""
        return "📅 *Yilni tanlang*\n\nKino chiqarilgan yilni tanlang:"

    @staticmethod
    def format_quality_filter() -> str:
        """Format quality filter selection message."""
        return "📺 *Sifatni tanlang*\n\nVideo sifatini tanlang:"

    @staticmethod
    def format_rating_filter() -> str:
        """Format rating filter selection message."""
        return "⭐ *Minimal reytingni tanlang*\n\nFaqat shu reytingdan yuqori kinolar ko'rsatiladi:"

    @staticmethod
    def format_sort_options() -> str:
        """Format sort options message."""
        return "🔄 *Saralash*\n\nNatijalarni qanday saralash kerak:"

    @staticmethod
    def format_quick_search_help() -> str:
        """Format quick search help message."""
        lines = [
            "🔍 *Qidiruv*",
            "",
            "Kino kodini yoki nomini yuboring:",
            "",
            "📝 *Misollar:*",
            "• `123` \\- kod bo'yicha",
            "• `Qasoskorlar` \\- nom bo'yicha",
            "• `Marvel 2023` \\- nom \\+ yil",
            "",
            "Yoki quyidagilardan birini tanlang:",
        ]
        return "\n".join(lines)

    @staticmethod
    def format_search_hint() -> str:
        """Format search hint for main menu."""
        return "💡 Kino kodini yoki nomini yuboring"

    @staticmethod
    def _format_movie_item(movie: MovieDTO, index: int) -> str:
        """
        Format single movie item for list.

        Args:
            movie: Movie DTO
            index: Item index

        Returns:
            Formatted item string
        """
        title = SearchView._escape_md(movie.title[:35])
        if len(movie.title) > 35:
            title += "\\.\\.\\."

        parts = [f"{index}\\. `{movie.code}` — {title}"]

        details = []

        if movie.year:
            details.append(str(movie.year))

        if movie.quality:
            details.append(movie.quality)

        if movie.rating_count > 0:
            details.append(f"⭐{float(movie.average_rating):.1f}")

        if movie.is_series:
            details.append("📺")

        if details:
            parts.append(f"   _{' • '.join(details)}_")

        return "\n".join(parts)

    @staticmethod
    def _format_applied_filters(filters: SearchFilters) -> str:
        """
        Format applied filters as string.

        Args:
            filters: Search filters

        Returns:
            Formatted filters string
        """
        parts = []

        if filters.year:
            parts.append(f"📅 {filters.year}")
        elif filters.year_from or filters.year_to:
            year_range = f"{filters.year_from or '...'}-{filters.year_to or '...'}"
            parts.append(f"📅 {year_range}")

        if filters.quality:
            parts.append(f"📺 {filters.quality}")

        if filters.min_rating:
            parts.append(f"⭐ {filters.min_rating}+")

        if filters.series_only:
            parts.append("📺 Seriallar")

        if filters.sort_by != "relevance":
            sort_labels = {
                "rating": "⭐ Reyting",
                "downloads": "📥 Yuklanish",
                "newest": "🆕 Yangi",
            }
            parts.append(sort_labels.get(filters.sort_by, ""))

        return " | ".join(parts) if parts else "Yo'q"

    @staticmethod
    def _escape_md(text: str) -> str:
        """Escape MarkdownV2 special characters."""
        chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        for char in chars:
            text = text.replace(char, f"\\{char}")
        return text
