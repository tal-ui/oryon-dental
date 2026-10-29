"""Database configuration and session management."""

import os
from collections.abc import AsyncGenerator
from datetime import UTC, datetime

from sqlalchemy import DateTime
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.pool import NullPool

from app.config import settings


def _flag(name: str) -> bool:
    return os.getenv(name, "").lower() in {"1", "true", "yes", "require"}


# Serverless hosts (Vercel) cannot keep SQLAlchemy's queue pool: each
# instance would hold pool_size connections, and Supavisor transaction
# mode rejects asyncpg's prepared-statement cache. Set DB_SERVERLESS=true
# there. DB_SSL=require turns on TLS for the pooler, which asyncpg does
# not infer from the URL. Local Docker leaves both unset.
_connect_args: dict[str, object] = {}
if _flag("DB_SSL"):
    _connect_args["ssl"] = "require"
if _flag("DB_SERVERLESS"):
    _connect_args["statement_cache_size"] = 0

_engine_kwargs: dict[str, object] = {
    "pool_pre_ping": True,
    "echo": settings.ENVIRONMENT == "development",
    "connect_args": _connect_args,
}
if _flag("DB_SERVERLESS"):
    _engine_kwargs["poolclass"] = NullPool
else:
    # ``pool_pre_ping`` issues a cheap ``SELECT 1`` before checking out a
    # connection so stale sockets (DB restart, NAT/firewall idle drop) are
    # transparently recycled instead of failing the next request with a
    # generic "connection lost". ``pool_recycle=3600`` ages connections out
    # proactively so we don't accumulate idle ones a proxy might silently
    # close.
    _engine_kwargs.update(
        pool_size=10,
        max_overflow=20,
        pool_timeout=30,
        pool_recycle=3600,
    )

engine = create_async_engine(settings.DATABASE_URL, **_engine_kwargs)

# ``expire_on_commit=False`` keeps ORM objects hydrated after a commit
# so the router can serialise the response without an extra refresh
# round-trip. Anything streaming or kept across awaits (long-lived
# tasks, websockets) must re-fetch explicitly — but the request-scoped
# pattern that dominates the codebase relies on this.
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass


class TimestampMixin:
    """Mixin that adds created_at and updated_at columns."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that provides a database session."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database tables. For development only."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
