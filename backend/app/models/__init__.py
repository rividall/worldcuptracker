from app.core.database import Base  # noqa: F401 — needed for Alembic

from app.models.team import Team  # noqa: F401
from app.models.match import Match  # noqa: F401
from app.models.standing import GroupStanding  # noqa: F401
from app.models.scorer import Scorer  # noqa: F401
from app.models.sync_run import SyncRun  # noqa: F401
