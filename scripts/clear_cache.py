
import asyncio
from src.bot.loader import redis

async def clear_cache():
    print("🗑 Clearing Redis Cache...")
    try:
        await redis.flushdb()
        print("✅ Redis Cache Cleared!")
    except Exception as e:
        print(f"❌ Error clearing Redis: {e}")
    finally:
        await redis.aclose()

if __name__ == "__main__":
    asyncio.run(clear_cache())
