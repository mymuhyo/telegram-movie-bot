
import asyncio
from src.bot.loader import redis
from src.infrastructure.database import async_session_factory
from src.infrastructure import UnitOfWork
from src.core.config import settings

async def verify_cache():
    print("🚀 Starting Cache Verification")
    
    # Initialize UoW with Redis
    uow = UnitOfWork(async_session_factory, redis)
    
    async with uow:
        # 1. Get a popular movie code (or create dummy if needed, but assuming popular exists)
        movies = await uow.movies.get_popular(1)
        if not movies:
            print("❌ No movies found to test cache.")
            return

        movie = movies[0]
        code = movie.code
        print(f"🎬 Testing with Movie: {movie.title} (Code: {code})")
        
        # Clear cache first to be sure
        await redis.delete(f"movie:code:{code}")
        
        # 2. First fetch (DB Hit)
        print("1️⃣ First Fetch (Should be DB Hit)...")
        m1 = await uow.movies.get_by_code(code)
        assert m1 is not None
        
        # Check if key exists in Redis
        is_cached = await redis.exists(f"movie:code:{code}")
        print(f"   Cache Key Exists? {'✅ Yes' if is_cached else '❌ No'}")
        
        # 3. Second fetch (Cache Hit)
        print("2️⃣ Second Fetch (Should be Cache Hit)...")
        m2 = await uow.movies.get_by_code(code)
        assert m2 is not None
        assert m1.id == m2.id
        print("   ✅ Fetched successfully")

        # 4. Invalidation Test
        print("3️⃣ Testing Invalidation on Update...")
        m2.title = m2.title + " (Cached)"
        await uow.movies.update(m2)
        # Check if key deleted
        is_cached_after_update = await redis.exists(f"movie:code:{code}")
        print(f"   Cache Key Deleted? {'✅ Yes' if not is_cached_after_update else '❌ No'}")
        
        # Cleanup
        m2.title = movie.title.replace(" (Cached)", "")
        await uow.movies.update(m2)
    
    print("🎉 Verification Complete!")

if __name__ == "__main__":
    asyncio.run(verify_cache())
