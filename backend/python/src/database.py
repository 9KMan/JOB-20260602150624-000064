"""SQLAlchemy database setup and session management."""

from collections.abc import Generator
from contextlib import contextmanager
from typing import Annotated

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase
from sqlalchemy.pool import QueuePool

from src.config import get_settings


class Base(DeclarativeBase):
    """SQLAlchemy declarative base model."""

    type_annotation_map = {
        str: Annotated[str, "text"],
    }


class DatabaseManager:
    """Database connection and session manager."""

    def __init__(self) -> None:
        """Initialize database manager."""
        self._engine: Engine | None = None
        self._session_factory: sessionmaker[Session] | None = None

    def init(self) -> None:
        """Initialize database engine and session factory."""
        settings = get_settings()

        self._engine = create_engine(
            settings.database.database_url,
            poolclass=QueuePool,
            pool_size=settings.database.db_pool_size,
            max_overflow=settings.database.db_max_overflow,
            pool_timeout=settings.database.db_pool_timeout,
            pool_recycle=settings.database.db_pool_recycle,
            echo=settings.database.db_echo,
            pool_pre_ping=True,
        )

        self._session_factory = sessionmaker(
            bind=self._engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )

        @event.listens_for(self._engine, "connect")
        def set_search_path(dbapi_connection: object, connection_record: object) -> None:
            """Set PostgreSQL search path on connection."""
            pass

    @property
    def engine(self) -> Engine:
        """Get database engine."""
        if self._engine is None:
            self.init()
        assert self._engine is not None
        return self._engine

    @property
    def session_factory(self) -> sessionmaker[Session]:
        """Get session factory."""
        if self._session_factory is None:
            self.init()
        assert self._session_factory is not None
        return self._session_factory

    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        """Get a database session context manager."""
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_session(self) -> Generator[Session, None, None]:
        """FastAPI dependency for database session."""
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


db_manager = DatabaseManager()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for database session."""
    yield from db_manager.get_session()