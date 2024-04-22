from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import TIMESTAMP, Enum, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column
from sqlalchemy.sql import func

from src.application.services.database import Password, Status


class Base(DeclarativeBase):
    type_annotation_map = {
        datetime: TIMESTAMP(timezone=True),
        Status: Enum(Status, length=16),
    }

    id: Mapped[UUID] = mapped_column(
        primary_key=True, index=True, default=func.gen_random_uuid()
    )
    created: Mapped[datetime] = mapped_column(default=datetime.now(tz=timezone.utc))
    modified: Mapped[datetime] = mapped_column(
        default=datetime.now(tz=timezone.utc), onupdate=datetime.now(tz=timezone.utc)
    )

    async def async_create(self, session: AsyncSession):
        session.add(self)
        await session.commit()
        await session.refresh(self)
        return self

    @classmethod
    def sync_get(cls, session: Session, **kwargs):
        return session.scalar(select(cls).filter_by(**kwargs))

    @classmethod
    async def async_get(cls, session: AsyncSession, **kwargs):
        return await session.scalar(select(cls).filter_by(**kwargs))


__all__ = ("Base", "Status", "Password")
