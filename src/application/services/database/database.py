import logging
from typing import AsyncIterator

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.application.core import context

async_engine = create_async_engine(
    context.settings.db.url,
    **context.settings.db.connection_kwargs,
)

async_session = async_sessionmaker(
    bind=async_engine,
    **context.settings.db.session_kwargs,
)

sync_engine = create_engine(
    context.settings.db.url_sync,
    **context.settings.db.connection_kwargs,
)
session = sessionmaker(
    bind=sync_engine,
    **context.settings.db.session_kwargs,
)


async def yield_async_session() -> AsyncIterator[async_sessionmaker]:
    try:
        yield async_session()
    except SQLAlchemyError as e:
        logging.exception(e)


def get_sync_session():
    return session()


__all__ = ("yield_async_session", "get_sync_session")
