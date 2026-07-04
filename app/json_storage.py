from datetime import datetime, timedelta, timezone
from pathlib import Path
import json

from app.models import Product


class JsonStorage:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text(json.dumps({"users": [], "products": {}, "prices": []}), encoding="utf-8")

    def load(self) -> dict:
        return json.loads(self.path.read_text(encoding="utf-8"))

    def save(self, data: dict) -> None:
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    async def init(self) -> None:
        return None

    async def add_user(self, telegram_id: int) -> None:
        data = self.load()
        if telegram_id not in data["users"]:
            data["users"].append(telegram_id)
        self.save(data)

    async def get_users(self) -> list[int]:
        return [int(x) for x in self.load()["users"]]

    async def upsert_product(self, product: Product) -> None:
        data = self.load()
        key = f"{product.marketplace}:{product.product_id}"
        data["products"][key] = {
            "marketplace": product.marketplace,
            "product_id": product.product_id,
            "category": product.category,
            "title": product.title,
            "price": product.current_price,
            "url": product.url,
        }
        self.save(data)

    async def add_price(self, product: Product) -> None:
        data = self.load()
        data["prices"].append({
            "marketplace": product.marketplace,
            "product_id": product.product_id,
            "price": product.current_price,
            "collected_at": datetime.now(timezone.utc).isoformat(),
        })
        self.save(data)

    async def get_recent_prices(self, marketplace: str, product_id: str, days: int = 30) -> list[float]:
        since = datetime.now(timezone.utc) - timedelta(days=days)
        rows = []
        for item in self.load()["prices"]:
            same_product = item["marketplace"] == marketplace and item["product_id"] == product_id
            recent = datetime.fromisoformat(item["collected_at"]) >= since
            if same_product and recent:
                rows.append(float(item["price"]))
        return rows
