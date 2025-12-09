"""Series view for formatting series-related messages."""

from src.application.dto import SeriesDTO, SeriesWithPartsDTO, UserSeriesProgressDTO


class SeriesView:
    """Formats series data for display in Telegram."""

    @staticmethod
    def format_series_header(series: SeriesDTO) -> str:
        """
        Format series header.

        Args:
            series: Series DTO

        Returns:
            Formatted header
        """
        lines = [f"📺 *{SeriesView._escape_md(series.name)}*", ""]

        if series.description:
            desc = series.description[:200]
            if len(series.description) > 200:
                desc += "..."
            lines.append(f"📝 {SeriesView._escape_md(desc)}")
            lines.append("")

        lines.append(f"📊 Qismlar: {series.available_parts}/{series.total_parts}")

        if series.is_complete:
            lines.append("✅ To'liq")
        else:
            lines.append(f"⏳ {series.total_parts - series.available_parts} qism kutilmoqda")

        return "\n".join(lines)

    @staticmethod
    def format_series_with_progress(
        series_data: SeriesWithPartsDTO,
        progress: UserSeriesProgressDTO | None = None,
    ) -> str:
        """
        Format series info with user progress.

        Args:
            series_data: Series with parts data
            progress: User's progress

        Returns:
            Formatted message
        """
        series = series_data.series
        lines = [f"📺 *{SeriesView._escape_md(series.name)}*", ""]

        # Description
        if series.description:
            desc = series.description[:150]
            if len(series.description) > 150:
                desc += "..."
            lines.append(f"📝 {SeriesView._escape_md(desc)}")
            lines.append("")

        # Parts count
        lines.append(f"📊 Mavjud qismlar: {series.available_parts}")

        # Progress info
        if progress:
            lines.append("")
            watched = progress.watched_count
            total = progress.total_parts
            percent = int(progress.progress_percentage)

            # Progress bar
            filled = int(percent / 10)
            empty = 10 - filled
            progress_bar = "█" * filled + "░" * empty

            lines.append(f"▶️ *Sizning progressingiz:*")
            lines.append(f"   {progress_bar} {percent}%")
            lines.append(f"   Ko'rilgan: {watched}/{total} qism")

            if progress.next_unwatched:
                lines.append(f"   ▶️ Keyingi qism: {progress.next_unwatched}")

            if percent >= 100:
                lines.append("")
                lines.append("✅ *Serial to'liq ko'rilgan!*")

        lines.append("")
        lines.append("⬇️ Qismni tanlang:")

        return "\n".join(lines)

    @staticmethod
    def format_series_list_header() -> str:
        """Format series list header."""
        return "📺 *Barcha seriallar*\n\nQuyidagi seriallarni tanlang:"

    @staticmethod
    def format_in_progress_header() -> str:
        """Format in-progress series header."""
        return "▶️ *Davom etish*\n\nKo'rib turgan seriallaringiz:"

    @staticmethod
    def format_part_info(
        series_data: SeriesWithPartsDTO,
        part_number: int,
    ) -> str:
        """
        Format part info for display.

        Args:
            series_data: Full series data
            part_number: Current part number

        Returns:
            Part info string
        """
        series = series_data.series
        return f"📺 {series.name} | {part_number}/{series.total_parts}-qism"

    @staticmethod
    def format_progress_updated(
        series_name: str,
        part_number: int,
        total_parts: int,
        watched_count: int,
    ) -> str:
        """
        Format progress update notification.

        Args:
            series_name: Series name
            part_number: Just watched part
            total_parts: Total parts
            watched_count: Total watched count

        Returns:
            Progress update message
        """
        percent = int((watched_count / total_parts) * 100)
        progress_bar = "█" * (percent // 10) + "░" * (10 - percent // 10)

        lines = [
            f"✅ *{part_number}\\-qism ko'rildi!*",
            "",
            f"📺 {SeriesView._escape_md(series_name)}",
            f"📊 Progress: {progress_bar} {percent}%",
        ]

        if watched_count >= total_parts:
            lines.append("")
            lines.append("🎉 *Tabriklaymiz! Serial to'liq ko'rildi!*")

        return "\n".join(lines)

    @staticmethod
    def format_empty_series_list() -> str:
        """Format empty series list message."""
        return "📭 *Seriallar topilmadi*\n\nHozircha seriallar mavjud emas."

    @staticmethod
    def format_no_progress() -> str:
        """Format no progress message."""
        lines = [
            "📭 *Davom etish uchun seriallar yo'q*",
            "",
            "Serial ko'rishni boshlang, va bu yerda davom ettirish imkoniyati paydo bo'ladi.",
        ]
        return "\n".join(lines)

    @staticmethod
    def _escape_md(text: str) -> str:
        """Escape markdown special characters."""
        chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        for char in chars:
            text = text.replace(char, f"\\{char}")
        return text
