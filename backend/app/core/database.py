from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
import os

# Database URL - uses internal container port (5432) when running in Docker
# For local development outside Docker, use port 5435
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://harvestnet:password123@localhost:5435/harvestnet"  # Changed to 5435
)

# Create engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Set to False in production
    pool_size=10,
    max_overflow=20
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base class for models
Base = declarative_base()

async def get_db():
    """Dependency for getting database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_db():
    """Initialize database - create tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(seed_default_data)

def seed_default_data(sync_conn):
    """Seed default data if needed"""
    from sqlalchemy import inspect, text
    
    inspector = inspect(sync_conn)
    if 'farms' in inspector.get_table_names():
        result = sync_conn.execute(text("SELECT COUNT(*) FROM farms"))
        count = result.scalar()
        
        if count == 0:
            sync_conn.execute(
                text("""
                    INSERT INTO farms (id, name, location, created_at)
                    VALUES ('demo-farm-1', 'Demo Farm', 'Sample Location', NOW())
                """)
            )
            print("Demo farm created")