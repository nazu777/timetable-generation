import json
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql+psycopg://timetable:timetable_dev_pw@localhost:5432/timetable"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"
    BACKEND_CORS_ORIGINS: str = '["http://localhost:5173"]'
    SECRET_KEY: str = "change-me"
    SOLVER_TIME_LIMIT_SECONDS: int = 30

    @property
    def cors_origins_list(self) -> list[str]:
        try:
            return json.loads(self.BACKEND_CORS_ORIGINS)
        except Exception:
            return ["http://localhost:5173"]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
