from __future__ import annotations

from dataclasses import replace
from random import Random

import httpx

from app.models import Product


class BaseCollector:
    marketplace: str

    async def collect_category(self, category: str, limit: int) -> list[Product]:
        raise NotImplementedError


class DemoCollector(BaseCollector):
    """Deterministic demo data for local testing without marketplace scraping."""

    marketplace = "demo"

    async def collect_category(self, category: str, limit: int) -> list[Product]:
        rnd = Random(category)
        products: list[Product] = []
        for index in range(min(limit, 25)):
            base = rnd.randint(2_000, 80_000)
            price = base * (0.72 if index % 9 == 0 else rnd.uniform(0.92, 1.06))
            products.append(
                Product(
                    marketplace=self.marketplace,
                    category=category,
                    product_id=f"{category}-{index}",
                    title=f"Demo {category} #{index + 1}",
                    current_price=round(price, 2),
                    url="https://example.com/product/" + f"{category}-{index}",
                    image_url=None,
                    brand="DemoBrand",
                    rating=4.7,
                    review_count=100 + index,
                    available=True,
                )
            )
        return products


class OzonCollector(BaseCollector):
    marketplace = "ozon"

    def __init__(self, user_agent: str = "Mozilla/5.0"):
        self.user_agent = user_agent

    async def collect_category(self, category: str, limit: int) -> list[Product]:
        # TODO: inspect current Ozon catalog XHR calls and map them here.
        # Keep request volume low, cache responses and respect marketplace rules.
        return []


class WildberriesCollector(BaseCollector):
    marketplace = "wildberries"

    def __init__(self, user_agent: str = "Mozilla/5.0"):
        self.user_agent = user_agent

    async def collect_category(self, category: str, limit: int) -> list[Product]:
        # TODO: adapt to current WB catalog endpoints or Playwright flow.
        # Use backoff, proxy rotation and category-level scheduling in production.
        return []
