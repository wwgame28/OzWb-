from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    telegram_bot_token: str
    database_path: Path = Path("data/prices.db")
    rare_discount_threshold: float = 0.20
    min_history_points: int = 10
    scan_interval_hours: int = 24
    top_limit_per_category: int = 1000
    default_categories: str = "smartphones,coffee-machines,sneakers"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def categories(self) -> list[str]:
        return [item.strip() for item in self.default_categories.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
