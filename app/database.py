"""
Database Configuration Module

This module handles database connections and session management for:
- PostgreSQL (via SQLAlchemy async)
- Redis (for caching and session management)
"""

from typing import AsyncGenerator, Generator, Optional
from contextlib import asynccontextmanager, contextmanager
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker
)
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.pool import NullPool
import redis.asyncio as aioredis
from redis.asyncio import Redis
import logging

from app.config import settings


logger = logging.getLogger(__name__)


# =============================================================================
# SQLAlchemy Base
# =============================================================================

Base = declarative_base()


# =============================================================================
# Database Engine & Session
# =============================================================================

class DatabaseManager:
    """
    Manages database connections and sessions for PostgreSQL.

    Attributes:
        engine: SQLAlchemy async engine
        async_session_maker: Session factory for creating database sessions
    """

    def __init__(self) -> None:
        """Initialize database manager with engine and session factory."""
        self.engine: Optional[AsyncEngine] = None
        self.sync_engine = None
        self.async_session_maker: Optional[async_sessionmaker] = None
        self.sync_session_maker = None

    def init_db(self) -> None:
        """
        Initialize database engine and session factory.

        This method configures both async and sync SQLAlchemy engines with connection pooling
        and creates session factories for database operations.
        """
        # Convert async URL to sync URL
        sync_database_url = settings.DATABASE_URL.replace(
            "postgresql+asyncpg://", "postgresql+psycopg2://"
        )

        # Create async engine (poolclass auto-selected for async)
        if settings.is_testing:
            # Use NullPool for testing
            self.engine = create_async_engine(
                settings.DATABASE_URL,
                echo=settings.DB_ECHO,
                poolclass=NullPool,
            )
            self.sync_engine = create_engine(
                sync_database_url,
                echo=settings.DB_ECHO,
                poolclass=NullPool,
            )
        else:
            # Use default async pool with configuration
            self.engine = create_async_engine(
                settings.DATABASE_URL,
                echo=settings.DB_ECHO,
                pool_size=settings.DB_POOL_SIZE,
                max_overflow=settings.DB_MAX_OVERFLOW,
                pool_timeout=settings.DB_POOL_TIMEOUT,
                pool_recycle=settings.DB_POOL_RECYCLE,
                pool_pre_ping=True,  # Verify connections before using
            )
            # Create sync engine
            self.sync_engine = create_engine(
                sync_database_url,
                echo=settings.DB_ECHO,
                pool_size=settings.DB_POOL_SIZE,
                max_overflow=settings.DB_MAX_OVERFLOW,
                pool_timeout=settings.DB_POOL_TIMEOUT,
                pool_recycle=settings.DB_POOL_RECYCLE,
                pool_pre_ping=True,
            )

        # Create session factories
        self.async_session_maker = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )

        self.sync_session_maker = sessionmaker(
            self.sync_engine,
            class_=Session,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )

        logger.info(
            f"Database initialized: {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
        )

    async def close_db(self) -> None:
        """
        Close database connections and dispose of the engines.

        This should be called during application shutdown.
        """
        if self.engine:
            await self.engine.dispose()
        if self.sync_engine:
            self.sync_engine.dispose()
        logger.info("Database connections closed")

    async def create_tables(self) -> None:
        """
        Create all database tables.

        Note: In production, use Alembic migrations instead.
        This is mainly for development and testing.
        """
        if not self.engine:
            raise RuntimeError("Database not initialized. Call init_db() first.")

        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created")

    async def drop_tables(self) -> None:
        """
        Drop all database tables.

        Warning: This will delete all data! Use with caution.
        Only for development and testing.
        """
        if not self.engine:
            raise RuntimeError("Database not initialized. Call init_db() first.")

        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            logger.info("Database tables dropped")

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get a database session as an async context manager.

        Yields:
            AsyncSession: Database session

        Example:
            async with db_manager.get_session() as session:
                result = await session.execute(query)
        """
        if not self.async_session_maker:
            raise RuntimeError("Database not initialized. Call init_db() first.")

        async with self.async_session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error(f"Database session error: {e}")
                raise
            finally:
                await session.close()


# =============================================================================
# Redis Connection Manager
# =============================================================================

class RedisManager:
    """
    Manages Redis connections for caching and session management.

    Attributes:
        redis_client: Redis async client instance
    """

    def __init__(self) -> None:
        """Initialize Redis manager."""
        self.redis_client: Optional[Redis] = None

    async def init_redis(self) -> None:
        """
        Initialize Redis connection.

        Creates a connection pool and Redis client for async operations.
        """
        try:
            self.redis_client = await aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                max_connections=settings.REDIS_MAX_CONNECTIONS,
                socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
                socket_connect_timeout=settings.REDIS_SOCKET_CONNECT_TIMEOUT,
            )

            # Test connection
            await self.redis_client.ping()
            logger.info(
                f"Redis initialized: {settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
            )

        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            raise

    async def close_redis(self) -> None:
        """
        Close Redis connection.

        This should be called during application shutdown.
        """
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Redis connection closed")

    async def get_redis(self) -> Redis:
        """
        Get Redis client instance.

        Returns:
            Redis: Redis client

        Raises:
            RuntimeError: If Redis is not initialized
        """
        if not self.redis_client:
            raise RuntimeError("Redis not initialized. Call init_redis() first.")
        return self.redis_client

    async def set_value(
        self,
        key: str,
        value: str,
        expire: Optional[int] = None
    ) -> bool:
        """
        Set a value in Redis with optional expiration.

        Args:
            key: Redis key
            value: Value to store
            expire: Expiration time in seconds (optional)

        Returns:
            bool: True if successful
        """
        redis = await self.get_redis()
        result = await redis.set(key, value)

        if expire:
            await redis.expire(key, expire)

        return result

    async def get_value(self, key: str) -> Optional[str]:
        """
        Get a value from Redis.

        Args:
            key: Redis key

        Returns:
            Optional[str]: Value if exists, None otherwise
        """
        redis = await self.get_redis()
        return await redis.get(key)

    async def delete_value(self, key: str) -> int:
        """
        Delete a value from Redis.

        Args:
            key: Redis key

        Returns:
            int: Number of keys deleted
        """
        redis = await self.get_redis()
        return await redis.delete(key)

    async def exists(self, key: str) -> bool:
        """
        Check if a key exists in Redis.

        Args:
            key: Redis key

        Returns:
            bool: True if key exists
        """
        redis = await self.get_redis()
        return bool(await redis.exists(key))

    async def set_hash(self, key: str, mapping: dict, expire: Optional[int] = None) -> bool:
        """
        Set a hash in Redis.

        Args:
            key: Redis key
            mapping: Dictionary of field-value pairs
            expire: Expiration time in seconds (optional)

        Returns:
            bool: True if successful
        """
        redis = await self.get_redis()
        result = await redis.hset(key, mapping=mapping)

        if expire:
            await redis.expire(key, expire)

        return result

    async def get_hash(self, key: str) -> dict:
        """
        Get a hash from Redis.

        Args:
            key: Redis key

        Returns:
            dict: Hash contents
        """
        redis = await self.get_redis()
        return await redis.hgetall(key)


# =============================================================================
# Global Instances
# =============================================================================

# Create singleton instances
db_manager = DatabaseManager()
redis_manager = RedisManager()


# =============================================================================
# Dependency Injection for FastAPI
# =============================================================================

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for getting async database sessions.

    Yields:
        AsyncSession: Database session

    Example:
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(User))
            return result.scalars().all()
    """
    if not db_manager.async_session_maker:
        raise RuntimeError("Database not initialized")

    async with db_manager.async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()


def get_sync_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency for getting sync database sessions.

    Yields:
        Session: Database session

    Example:
        @app.get("/palettes")
        async def get_palettes(db: Session = Depends(get_sync_db)):
            palettes = db.query(Palette).all()
            return palettes
    """
    if not db_manager.sync_session_maker:
        raise RuntimeError("Database not initialized")

    session = db_manager.sync_session_maker()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        session.close()


async def get_redis() -> Redis:
    """
    FastAPI dependency for getting Redis client.

    Returns:
        Redis: Redis client instance

    Example:
        @app.get("/cache")
        async def get_cache(redis: Redis = Depends(get_redis)):
            value = await redis.get("key")
            return {"value": value}
    """
    return await redis_manager.get_redis()


# =============================================================================
# Application Lifecycle Management
# =============================================================================

async def init_databases() -> None:
    """
    Initialize all database connections.

    This should be called during application startup.
    """
    logger.info("Initializing databases...")

    # Initialize PostgreSQL
    db_manager.init_db()

    # Initialize Redis
    await redis_manager.init_redis()

    logger.info("All databases initialized successfully")


async def close_databases() -> None:
    """
    Close all database connections.

    This should be called during application shutdown.
    """
    logger.info("Closing database connections...")

    # Close PostgreSQL
    await db_manager.close_db()

    # Close Redis
    await redis_manager.close_redis()

    logger.info("All database connections closed")
