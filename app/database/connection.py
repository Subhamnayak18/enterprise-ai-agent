import logging
from functools import lru_cache

from sqlalchemy import Engine, create_engine, event, text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import get_settings

logger = logging.getLogger(__name__)


@lru_cache
def get_engine() -> Engine:
    settings = get_settings()
    url = settings.database_url
    if url.startswith("sqlite"):
        engine = create_engine(url, connect_args={"check_same_thread": False})
        return engine

    engine = create_engine(
        url,
        pool_pre_ping=True,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
        connect_args={"connect_timeout": settings.database_connect_timeout_seconds},
    )
    return engine


def check_database_connection() -> bool:
    try:
        with get_engine().connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except (SQLAlchemyError, OSError) as exc:
        logger.warning("Database health check failed: %s", type(exc).__name__)
        return False
