"""Search keyboard builder."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.application.dto import MovieDTO, SearchFilters, SearchResult


class SearchKeyboard:
    """Keyboard builder for search functionality."""

    # Available years for filter
    YEARS = [2024, 2023, 2022, 2021, 2020, "2015-2019", "2010-2014", "< 2010"]

    # Available qualities
    QUALITIES = ["4K", "1080p", "720p", "480p"]

    # Sort options
    SORT_OPTIONS = [
        ("relevance", "📊 Mos kelishi"),
        ("rating", "⭐ Reyting"),
        ("downloads", "📥 Yuklanish"),
        ("newest", "🆕 Yangi"),
    ]

    @staticmethod
    def get_search_results_keyboard(
        result: SearchResult,
    ) -> InlineKeyboardMarkup:
        """
        Get keyboard for search results.

        Args:
            result: Search result with movies

        Returns:
            Inline keyboard with movie buttons and pagination
        """
        buttons = []

        # Movie buttons
        for movie in result.movies:
            rating = ""
            if movie.rating_count > 0:
                rating = f" ⭐{float(movie.average_rating):.1f}"

            title = movie.title[:30]
            if len(movie.title) > 30:
                title += "..."

            # Series indicator
            series = " 📺" if movie.is_series else ""

            buttons.append([
                InlineKeyboardButton(
                    text=f"🎬 {title}{series}{rating}",
                    callback_data=f"movie:{movie.code}",
                )
            ])

        # Pagination row
        if result.total_pages > 1:
            nav_row = []

            if result.page > 1:
                nav_row.append(
                    InlineKeyboardButton(
                        text="◀️",
                        callback_data=f"search:page:{result.page - 1}",
                    )
                )

            nav_row.append(
                InlineKeyboardButton(
                    text=f"{result.page}/{result.total_pages}",
                    callback_data="noop",
                )
            )

            if result.page < result.total_pages:
                nav_row.append(
                    InlineKeyboardButton(
                        text="▶️",
                        callback_data=f"search:page:{result.page + 1}",
                    )
                )

            buttons.append(nav_row)

        # Filter row
        filter_row = [
            InlineKeyboardButton(
                text="🔧 Filtrlar",
                callback_data="search:filters",
            ),
        ]

        if result.filters.has_filters:
            filter_row.append(
                InlineKeyboardButton(
                    text="❌ Tozalash",
                    callback_data="search:clear",
                )
            )

        buttons.append(filter_row)

        # Close button
        buttons.append([
            InlineKeyboardButton(
                text="❌ Yopish",
                callback_data="close",
            )
        ])

        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def get_filters_keyboard(
        current_filters: SearchFilters,
    ) -> InlineKeyboardMarkup:
        """
        Get filters selection keyboard.

        Args:
            current_filters: Currently applied filters

        Returns:
            Inline keyboard with filter options
        """
        buttons = []

        # Year filter
        year_text = "📅 Yil"
        if current_filters.year:
            year_text = f"📅 Yil: {current_filters.year}"
        elif current_filters.year_from or current_filters.year_to:
            year_text = f"📅 Yil: {current_filters.year_from or '...'}-{current_filters.year_to or '...'}"

        buttons.append([
            InlineKeyboardButton(
                text=year_text,
                callback_data="filter:year",
            )
        ])

        # Quality filter
        quality_text = "📺 Sifat"
        if current_filters.quality:
            quality_text = f"📺 Sifat: {current_filters.quality}"

        buttons.append([
            InlineKeyboardButton(
                text=quality_text,
                callback_data="filter:quality",
            )
        ])

        # Rating filter
        rating_text = "⭐ Min reyting"
        if current_filters.min_rating:
            rating_text = f"⭐ Min reyting: {current_filters.min_rating}+"

        buttons.append([
            InlineKeyboardButton(
                text=rating_text,
                callback_data="filter:rating",
            )
        ])

        # Series only toggle
        series_text = "📺 Faqat seriallar"
        if current_filters.series_only:
            series_text = "✅ Faqat seriallar"

        buttons.append([
            InlineKeyboardButton(
                text=series_text,
                callback_data="filter:series",
            )
        ])

        # Sort options
        current_sort = current_filters.sort_by
        sort_label = next(
            (label for key, label in SearchKeyboard.SORT_OPTIONS if key == current_sort),
            "📊 Saralash"
        )

        buttons.append([
            InlineKeyboardButton(
                text=f"🔄 {sort_label}",
                callback_data="filter:sort",
            )
        ])

        # Action buttons
        buttons.append([
            InlineKeyboardButton(
                text="✅ Qo'llash",
                callback_data="filter:apply",
            ),
            InlineKeyboardButton(
                text="❌ Bekor",
                callback_data="filter:cancel",
            ),
        ])

        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def get_year_filter_keyboard(
        current_year: int | None = None,
    ) -> InlineKeyboardMarkup:
        """
        Get year filter selection keyboard.

        Args:
            current_year: Currently selected year

        Returns:
            Inline keyboard with year options
        """
        buttons = []

        # Recent years (2 per row)
        recent_years = [2024, 2023, 2022, 2021, 2020, 2019]
        for i in range(0, len(recent_years), 2):
            row = []
            for year in recent_years[i:i + 2]:
                mark = "✅ " if current_year == year else ""
                row.append(
                    InlineKeyboardButton(
                        text=f"{mark}{year}",
                        callback_data=f"filter:year:{year}",
                    )
                )
            buttons.append(row)

        # Year ranges
        buttons.append([
            InlineKeyboardButton(
                text="2015-2019",
                callback_data="filter:year:2015-2019",
            ),
            InlineKeyboardButton(
                text="2010-2014",
                callback_data="filter:year:2010-2014",
            ),
        ])

        buttons.append([
            InlineKeyboardButton(
                text="< 2010",
                callback_data="filter:year:<2010",
            ),
            InlineKeyboardButton(
                text="Barchasi",
                callback_data="filter:year:all",
            ),
        ])

        # Back button
        buttons.append([
            InlineKeyboardButton(
                text="🔙 Orqaga",
                callback_data="search:filters",
            )
        ])

        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def get_quality_filter_keyboard(
        current_quality: str | None = None,
    ) -> InlineKeyboardMarkup:
        """
        Get quality filter selection keyboard.

        Args:
            current_quality: Currently selected quality

        Returns:
            Inline keyboard with quality options
        """
        buttons = []

        # Quality options (2 per row)
        for i in range(0, len(SearchKeyboard.QUALITIES), 2):
            row = []
            for quality in SearchKeyboard.QUALITIES[i:i + 2]:
                mark = "✅ " if current_quality == quality else ""
                row.append(
                    InlineKeyboardButton(
                        text=f"{mark}{quality}",
                        callback_data=f"filter:quality:{quality}",
                    )
                )
            buttons.append(row)

        # All qualities
        buttons.append([
            InlineKeyboardButton(
                text="Barchasi",
                callback_data="filter:quality:all",
            )
        ])

        # Back button
        buttons.append([
            InlineKeyboardButton(
                text="🔙 Orqaga",
                callback_data="search:filters",
            )
        ])

        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def get_rating_filter_keyboard(
        current_rating: float | None = None,
    ) -> InlineKeyboardMarkup:
        """
        Get minimum rating filter keyboard.

        Args:
            current_rating: Currently selected minimum rating

        Returns:
            Inline keyboard with rating options
        """
        buttons = []

        ratings = [4.5, 4.0, 3.5, 3.0]

        for i in range(0, len(ratings), 2):
            row = []
            for rating in ratings[i:i + 2]:
                mark = "✅ " if current_rating == rating else ""
                stars = "⭐" * int(rating)
                row.append(
                    InlineKeyboardButton(
                        text=f"{mark}{stars} {rating}+",
                        callback_data=f"filter:rating:{rating}",
                    )
                )
            buttons.append(row)

        # All ratings
        buttons.append([
            InlineKeyboardButton(
                text="Barchasi",
                callback_data="filter:rating:all",
            )
        ])

        # Back button
        buttons.append([
            InlineKeyboardButton(
                text="🔙 Orqaga",
                callback_data="search:filters",
            )
        ])

        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def get_sort_keyboard(
        current_sort: str = "relevance",
    ) -> InlineKeyboardMarkup:
        """
        Get sort options keyboard.

        Args:
            current_sort: Currently selected sort option

        Returns:
            Inline keyboard with sort options
        """
        buttons = []

        for key, label in SearchKeyboard.SORT_OPTIONS:
            mark = "✅ " if current_sort == key else ""
            buttons.append([
                InlineKeyboardButton(
                    text=f"{mark}{label}",
                    callback_data=f"filter:sort:{key}",
                )
            ])

        # Back button
        buttons.append([
            InlineKeyboardButton(
                text="🔙 Orqaga",
                callback_data="search:filters",
            )
        ])

        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def get_quick_search_keyboard() -> InlineKeyboardMarkup:
        """
        Get quick search suggestions keyboard.

        Returns:
            Inline keyboard with quick search options
        """
        buttons = [
            [
                InlineKeyboardButton(
                    text="🔥 Mashhur",
                    callback_data="rec:popular",
                ),
                InlineKeyboardButton(
                    text="⭐ Yaxshilari",
                    callback_data="rec:top",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🆕 Yangi",
                    callback_data="rec:recent",
                ),
                InlineKeyboardButton(
                    text="📺 Seriallar",
                    callback_data="series:list",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🔧 Filtrlar bilan qidirish",
                    callback_data="search:filters",
                ),
            ],
        ]

        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def get_no_results_keyboard(
        query: str,
    ) -> InlineKeyboardMarkup:
        """
        Get keyboard when no results found.

        Args:
            query: Search query

        Returns:
            Inline keyboard with suggestions
        """
        buttons = [
            [
                InlineKeyboardButton(
                    text="🔧 Filtrlarni o'zgartiring",
                    callback_data="search:filters",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="📝 Kino so'rash",
                    callback_data="request:start",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🔥 Mashhur kinolar",
                    callback_data="rec:popular",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="❌ Yopish",
                    callback_data="close",
                ),
            ],
        ]

        return InlineKeyboardMarkup(inline_keyboard=buttons)
