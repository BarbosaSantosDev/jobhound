from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base_model import Base


class ProfileModel(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    headline: Mapped[str] = mapped_column(String(255), default="")
    seniority: Mapped[str] = mapped_column(String(16))
    primary_stack: Mapped[list[str]] = mapped_column(ARRAY(String))
    secondary_stack: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    preferred_locations: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    accepts_remote: Mapped[bool] = mapped_column(Boolean, default=True)
    summary: Mapped[str] = mapped_column(Text, default="")
    search: Mapped[dict] = mapped_column(JSONB, default=dict)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )