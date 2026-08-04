from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from .base_model import Base


class MatchModel(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id"), index=True)
    score: Mapped[int] = mapped_column(Integer, index=True)
    reasons: Mapped[list[str]] = mapped_column(ARRAY(String))
    red_flags: Mapped[list[str]] = mapped_column(ARRAY(String))
    evaluated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
