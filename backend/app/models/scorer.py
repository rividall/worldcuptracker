from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Scorer(Base):
    """A tournament top-scorer row from football-data.org's /scorers endpoint.

    Aggregate over the whole competition (goals/assists/penalties to date), not
    per-match — the free tier does not expose per-match goal events. Rebuilt in
    full each sync, like group_standings.
    """

    __tablename__ = "scorers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # football-data.org player id (external); not a PK because a player could in
    # principle appear twice if the feed changed teams — team_id disambiguates.
    player_id: Mapped[int] = mapped_column(Integer, index=True)
    player_name: Mapped[str] = mapped_column(String(120))
    nationality: Mapped[str | None] = mapped_column(String(60), nullable=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), index=True)
    goals: Mapped[int] = mapped_column(Integer, default=0)
    # assists / penalties are inconsistently populated by the provider (may be null).
    assists: Mapped[int | None] = mapped_column(Integer, nullable=True)
    penalties: Mapped[int | None] = mapped_column(Integer, nullable=True)
    played_matches: Mapped[int | None] = mapped_column(Integer, nullable=True)
