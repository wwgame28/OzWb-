from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    telegram_bot_token: str

    database_url: str = "sqlite+aiosqlite:///./data/prices.db"
    database_path: Path = Path("data/prices.json")

    rare_discount_threshold: float = 0.20
    min_history_points: int = 10
    scan_interval_hours: int = 24
    top_limit_per_category: int = 1000
    default_categories: str = "smartphones,coffee-machines,sneakers"

    enable_demo_collector: bool = True
    enable_ozon_collector: bool = False
    enable_wb_collector: bool = False
    request_timeout_seconds: float = 20.0
    min_request_delay_seconds: float = 1.5
    proxy_url: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def categories(self) -> list[str]:
        return [item.strip() for item in self.default_categories.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
