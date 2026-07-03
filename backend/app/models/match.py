from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Match(Base):
    __tablename__ = "matches"

    # football-data.org match id (external, not auto-increment)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    stage: Mapped[str] = mapped_column(String(20), index=True)
    group_name: Mapped[str | None] = mapped_column(String(2), nullable=True)
    utc_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(20), index=True)
    home_team_id: Mapped[int | None] = mapped_column(ForeignKey("teams.id"), nullable=True)
    away_team_id: Mapped[int | None] = mapped_column(ForeignKey("teams.id"), nullable=True)
    home_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    away_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    duration: Mapped[str] = mapped_column(String(20), default="REGULAR")
    penalties_home: Mapped[int | None] = mapped_column(Integer, nullable=True)
    penalties_away: Mapped[int | None] = mapped_column(Integer, nullable=True)
    winner_team_id: Mapped[int | None] = mapped_column(ForeignKey("teams.id"), nullable=True)
    last_updated: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
