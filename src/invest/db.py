"""DB 엔진과 스키마 정의. 스키마 변경은 반드시 Alembic 마이그레이션으로 한다."""

from datetime import datetime
from functools import lru_cache
from typing import Any

from sqlalchemy import BigInteger, DateTime, Engine, Index, Integer, Text, create_engine, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from invest.config import get_settings


class Base(DeclarativeBase):
    pass


class JobRun(Base):
    """예약 작업 실행 이력. 수집기의 '마지막 성공 시각' 판단에도 쓴다."""

    __tablename__ = "job_runs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    job: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text)  # running / success / failed
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    items: Mapped[int | None] = mapped_column(Integer)
    error: Mapped[str | None] = mapped_column(Text)
    meta: Mapped[dict[str, Any] | None] = mapped_column(JSONB)

    __table_args__ = (Index("ix_job_runs_job_started_at", "job", "started_at"),)


@lru_cache
def get_engine() -> Engine:
    return create_engine(get_settings().database_url, pool_pre_ping=True)
