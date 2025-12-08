"""Application constants."""

# Pagination
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 50

# Rate limiting
DEFAULT_RATE_LIMIT = 5
DEFAULT_RATE_WINDOW = 60

# Search
MIN_SEARCH_LENGTH = 2
MAX_SEARCH_RESULTS = 10

# Broadcast
BROADCAST_BATCH_SIZE = 30
BROADCAST_DELAY_MS = 50

# Cache TTL (seconds)
CACHE_TTL_SETTINGS = 300  # 5 minutes
CACHE_TTL_USER = 60  # 1 minute
CACHE_TTL_MOVIE = 120  # 2 minutes

# Admin roles
ROLE_SUPER_ADMIN = "super_admin"
ROLE_ADMIN = "admin"

# Request statuses
STATUS_PENDING = "pending"
STATUS_APPROVED = "approved"
STATUS_REJECTED = "rejected"
STATUS_ADDED = "added"

# Broadcast statuses
BROADCAST_PENDING = "pending"
BROADCAST_RUNNING = "running"
BROADCAST_PAUSED = "paused"
BROADCAST_COMPLETED = "completed"
BROADCAST_CANCELLED = "cancelled"
BROADCAST_FAILED = "failed"

# Download sources
SOURCE_CODE = "code"
SOURCE_SEARCH = "search"
SOURCE_SERIES = "series"

# Admin action types
ACTION_ADD_MOVIE = "add_movie"
ACTION_EDIT_MOVIE = "edit_movie"
ACTION_DELETE_MOVIE = "delete_movie"
ACTION_ADD_ADMIN = "add_admin"
ACTION_REMOVE_ADMIN = "remove_admin"
ACTION_BAN_USER = "ban_user"
ACTION_UNBAN_USER = "unban_user"
ACTION_BROADCAST = "broadcast"
ACTION_MAINTENANCE_ON = "maintenance_on"
ACTION_MAINTENANCE_OFF = "maintenance_off"
ACTION_SETTINGS_CHANGE = "settings_change"
ACTION_BACKUP = "backup"
