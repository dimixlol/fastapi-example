from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from src.application.services.database import Status

from ..base import Base


class Message(Base):
    __tablename__ = "message"
    path: Mapped[str] = mapped_column(nullable=True)
    status: Mapped[Status] = mapped_column(nullable=False, default=Status.pending)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="messages")

    @classmethod
    def compose_path(cls, _id: UUID) -> str:
        return f"{datetime.now(tz=timezone.utc).strftime('%Y-%m-%d')}/{_id}"

    @property
    def link(self):
        return f"s3://{self.path}"

    def to_uploaded(self, session: Session):
        self.status = Status.uploaded
        session.commit()
