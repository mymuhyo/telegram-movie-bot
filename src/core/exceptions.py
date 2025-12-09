"""Custom exceptions for the application."""


class BotException(Exception):
    """Base exception for all bot errors."""

    def __init__(
        self,
        message: str,
        user_message: str | None = None,
    ) -> None:
        self.message = message
        self.user_message = user_message or message
        super().__init__(message)


# Domain exceptions
class EntityNotFoundError(BotException):
    """Raised when an entity is not found in the database."""

    pass


class MovieNotFoundError(EntityNotFoundError):
    """Raised when a movie is not found."""

    def __init__(self, code: int) -> None:
        super().__init__(
            message=f"Movie with code {code} not found",
            user_message=f"❌ Kod {code} topilmadi",
        )
        self.code = code


class UserNotFoundError(EntityNotFoundError):
    """Raised when a user is not found."""

    pass


class SeriesNotFoundError(EntityNotFoundError):
    """Raised when a series is not found."""

    pass


# Access exceptions
class AccessDeniedError(BotException):
    """Raised when access is denied."""

    pass


class UserBannedError(AccessDeniedError):
    """Raised when a banned user tries to access the bot."""

    def __init__(self, reason: str | None = None) -> None:
        self.reason = reason
        super().__init__(
            message=f"User is banned: {reason}",
            user_message="🚫 Sizga bot bloklangan.",
        )


class NotAdminError(AccessDeniedError):
    """Raised when a non-admin tries to access admin features."""

    def __init__(self) -> None:
        super().__init__(
            message="User is not an admin",
            user_message="❌ Bu buyruq faqat adminlar uchun.",
        )


class NotSuperAdminError(AccessDeniedError):
    """Raised when an admin (not super) tries to access super admin features."""

    def __init__(self) -> None:
        super().__init__(
            message="User is not a super admin",
            user_message="❌ Bu buyruq faqat bosh admin uchun.",
        )


# Validation exceptions
class ValidationError(BotException):
    """Raised when validation fails."""

    pass


class DuplicateCodeError(ValidationError):
    """Raised when trying to create a movie with existing code."""

    def __init__(self, code: int, existing_title: str) -> None:
        super().__init__(
            message=f"Movie code {code} already exists: {existing_title}",
            user_message=f"❌ Bu kod band: {existing_title}\nBoshqa kod kiriting:",
        )
        self.code = code
        self.existing_title = existing_title


class SearchQueryTooShortError(ValidationError):
    """Raised when search query is too short."""

    def __init__(self, min_length: int = 2) -> None:
        super().__init__(
            message=f"Search query must be at least {min_length} characters",
            user_message=f"❌ Kamida {min_length} ta belgi kiriting",
        )


# Rate limiting
class RateLimitError(BotException):
    """Raised when rate limit is exceeded."""

    def __init__(self, seconds_remaining: int) -> None:
        super().__init__(
            message=f"Rate limit exceeded, {seconds_remaining}s remaining",
            user_message=f"⏳ Juda ko'p so'rov!\n\nIltimos, {seconds_remaining} soniya kuting.",
        )
        self.seconds_remaining = seconds_remaining


# Maintenance
class MaintenanceModeError(BotException):
    """Raised when bot is in maintenance mode."""

    def __init__(self, message: str) -> None:
        super().__init__(
            message="Bot is in maintenance mode",
            user_message=f"🔧 Bot vaqtincha ishlamayapti\n\n{message}\n\nUzr so'raymiz!",
        )


# Subscription
class SubscriptionRequiredError(BotException):
    """Raised when user is not subscribed to required channel."""

    def __init__(self, channel: str) -> None:
        super().__init__(
            message=f"User not subscribed to {channel}",
            user_message=f"🔐 Botdan foydalanish uchun kanalga obuna bo'ling:\n\n👉 {channel}",
        )
        self.channel = channel


# Database exceptions
class DatabaseError(BotException):
    """Raised when database operation fails."""

    def __init__(self, message: str = "Database error") -> None:
        super().__init__(
            message=message,
            user_message="❌ Ma'lumotlar bazasi xatosi. Keyinroq urinib ko'ring.",
        )


class CacheError(BotException):
    """Raised when cache operation fails."""

    def __init__(self, message: str = "Cache error") -> None:
        super().__init__(
            message=message,
            user_message="❌ Kesh xatosi. Keyinroq urinib ko'ring.",
        )


# File/Media exceptions
class FileNotFoundError(BotException):
    """Raised when file is not found."""

    def __init__(self, file_id: str | None = None) -> None:
        super().__init__(
            message=f"File not found: {file_id}",
            user_message="❌ Fayl topilmadi. Admin bilan bog'laning.",
        )


class FileTooLargeError(BotException):
    """Raised when file is too large."""

    def __init__(self, max_size_mb: int = 50) -> None:
        super().__init__(
            message=f"File too large (max {max_size_mb}MB)",
            user_message=f"❌ Fayl hajmi {max_size_mb}MB dan oshmasligi kerak.",
        )


# Request exceptions
class RequestNotFoundError(EntityNotFoundError):
    """Raised when a request is not found."""

    def __init__(self, request_id: str) -> None:
        super().__init__(
            message=f"Request {request_id} not found",
            user_message="❌ So'rov topilmadi.",
        )


class DuplicateRequestError(ValidationError):
    """Raised when duplicate request is submitted."""

    def __init__(self) -> None:
        super().__init__(
            message="Duplicate request",
            user_message="❌ Siz allaqachon bunday so'rov yuborgansiz.",
        )


# Favorite exceptions
class AlreadyInFavoritesError(ValidationError):
    """Raised when movie is already in favorites."""

    def __init__(self) -> None:
        super().__init__(
            message="Movie already in favorites",
            user_message="⚠️ Bu kino allaqachon sevimlilar ro'yxatida.",
        )


class NotInFavoritesError(ValidationError):
    """Raised when trying to remove movie not in favorites."""

    def __init__(self) -> None:
        super().__init__(
            message="Movie not in favorites",
            user_message="⚠️ Bu kino sevimlilar ro'yxatida emas.",
        )


# Rating exceptions
class InvalidRatingError(ValidationError):
    """Raised when rating is invalid."""

    def __init__(self, score: int) -> None:
        super().__init__(
            message=f"Invalid rating score: {score}",
            user_message="❌ Noto'g'ri baho. 1-5 orasida tanlang.",
        )


# Series exceptions
class SeriesPartNotFoundError(EntityNotFoundError):
    """Raised when series part is not found."""

    def __init__(self, series_name: str, part_number: int) -> None:
        super().__init__(
            message=f"Part {part_number} of {series_name} not found",
            user_message=f"❌ {series_name}ning {part_number}-qismi topilmadi.",
        )
