"""Thin async client for the football-data.org v4 API.

Shapes verified live on 2026-07-03 — see docs/research/football-data-analysis.md.
"""

import httpx

from app.core.config import settings

BASE_URL = "https://api.football-data.org/v4"


class FootballDataClient:
    def __init__(self, api_key: str | None = None) -> None:
        self._headers = {"X-Auth-Token": api_key or settings.FOOTBALL_DATA_API_KEY}

    async def _get(self, path: str) -> dict:
        async with httpx.AsyncClient(
            base_url=BASE_URL, headers=self._headers, timeout=30
        ) as client:
            response = await client.get(path)
            if response.status_code >= 400:
                # Surface the API's error body — bare status codes are useless in logs.
                raise RuntimeError(
                    f"football-data.org {response.status_code} on {path}: "
                    f"{response.text[:300]}"
                )
            return response.json()

    async def get_standings(self) -> dict:
        return await self._get(f"/competitions/{settings.FOOTBALL_DATA_COMPETITION}/standings")

    async def get_matches(self) -> dict:
        return await self._get(f"/competitions/{settings.FOOTBALL_DATA_COMPETITION}/matches")


def normalize_group(raw: str | None) -> str | None:
    """'GROUP_A' (matches) and 'Group A' (standings) → 'A'."""
    if not raw:
        return None
    return raw.replace("GROUP_", "").replace("Group ", "").strip() or None
