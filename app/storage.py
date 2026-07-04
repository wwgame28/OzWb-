from datetime import datetime, timedelta, timezone
from pathlib import Path
import json

from app.models import Product


class JsonStorage:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text(json.dumps({"users": [], "products": {}, "prices": [], "notifications": []}), encoding="utf-8")

    def _load(self) -> dict:
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _save(self, data: dict) -> None:
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    async def init(self) -> None:
        return None

    async def add_user(self, telegram_id: int) -> None:
        data = self._load()
        if telegram_id not in data["users"]:
            data["users"].append(telegram_id)
        self._save(data)

    async def get_users(self) -> list[int]:
        return [int(x) for x in self._load()["users"]]

    async def upsert_product(self, product: Product) -> None:
        data = self._load()
        key = f"{product.marketplace}:{product.product_id}"
        data["products"][key] = product.__dict__
        self._save(data)

    async def add_price(self, product: Product) -> None:
        data = self._load()
        data["prices"].append({
            "marketplace": product.marketplace,
            "product_id": product.product_id,
            "price": product.current_price,
            "collected_at": datetime.now(timezone.utc).isoformat(),
        })
        self._save(data)

    async def get_recent_prices(self, marketplace: str, product_id: str, days: int = 30) -> list[float]:
        since = datetime.now(timezone.utc) - timedelta(days=days)
        result = []
        for row in self._load()["prices"]:
            if row["marketplace"] == marketplace and row["product_id"] == product_id:
                if datetime.fromisoformat(row["collected_at"]) >= since:
                    result.append(float(row["price"]))
        return result
