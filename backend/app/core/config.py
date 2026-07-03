from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://worldcup:changeme@db:5432/worldcup"

    # Auth / JWT
    SECRET_KEY: str = "CHANGE_ME_TO_LONG_RANDOM_STRING"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    ALLOWED_ORIGINS: str = (
        "http://localhost:5173,http://localhost:3007,https://worldcup.buenalynch.com"
    )

    # App
    APP_NAME: str = "worldcup"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # File uploads
    UPLOAD_DIR: str = "/app/uploads"
    MAX_UPLOAD_SIZE_MB: int = 10

    # football-data.org sync
    FOOTBALL_DATA_API_KEY: str = "CHANGE_ME"
    FOOTBALL_DATA_COMPETITION: str = "WC"
    FETCH_INTERVAL_MINUTES: int = 60

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
