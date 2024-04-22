from sqlalchemy import String, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base


class User(Base):
    __tablename__ = "user"
    username: Mapped[str] = mapped_column(String(16), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    messages: Mapped["Message"] = relationship(back_populates="user")

    @classmethod
    async def async_exists(cls, session: AsyncSession, username: str, email: str):
        return bool(
            await session.scalar(
                select(cls).where((cls.username == username) | (cls.email == email))
            )
        )
