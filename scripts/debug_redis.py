
import asyncio
from redis.asyncio import Redis
from src.core.config import settings

async def check_redis():
    print(f"🕵️ Testing Redis Connection to: {settings.redis_url}")
    try:
        r = Redis.from_url(str(settings.redis_url), socket_connect_timeout=5)
        await r.ping()
        print("✅ Redis Connection Successful!")
        await r.aclose()
    except Exception as e:
        print(f"❌ Redis Connection Failed: {e}")

if __name__ == "__main__":
    asyncio.run(check_redis())
