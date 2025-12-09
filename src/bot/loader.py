"""Bot loader - creates bot and dispatcher instances."""

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from src.core.config import settings

# Create bot instance
bot = Bot(
    token=settings.bot_token,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)

# Initialize storage
# NOTE: Cloud Redis is unstable. Switched to MemoryStorage for stability.
# try:
#     if settings.redis_url and "localhost" not in str(settings.redis_url):
#          redis = Redis.from_url(
#              str(settings.redis_url),
#              socket_connect_timeout=10,
#              socket_timeout=10,
#              health_check_interval=30,
#              retry_on_timeout=True
#          )
#     else:
#          redis = Redis.from_url(str(settings.redis_url))
#     storage = RedisStorage(redis=redis)
# except Exception as e:
#     from aiogram.fsm.storage.memory import MemoryStorage
#     print(f"⚠️ Redis connection failed: {e}. Switching to MemoryStorage.")
#     redis = None
#     storage = MemoryStorage()

redis = None
storage = MemoryStorage()

# Create dispatcher
dp = Dispatcher(storage=storage)
