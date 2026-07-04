from aiogram import Bot

from app.collectors import BaseCollector
from app.discount import detect_rare_discount
from app.json_storage import JsonStorage


class Scanner:
    def __init__(self, storage: JsonStorage, collectors: list[BaseCollector], threshold: float, min_points: int):
        self.storage = storage
        self.collectors = collectors
        self.threshold = threshold
        self.min_points = min_points

    async def scan(self, categories: list[str]) -> list[dict]:
        findings: list[dict] = []
        for category in categories:
            for collector in self.collectors:
                products = await collector.collect_category(category, limit=1000)
                for product in products:
                    history = await self.storage.get_recent_prices(product.marketplace, product.product_id)
                    result = detect_rare_discount(
                        current_price=product.current_price,
                        historical_prices=history,
                        threshold=self.threshold,
                        min_points=self.min_points,
                    )
                    await self.storage.upsert_product(product)
                    await self.storage.add_price(product)
                    if product.available and result.get("is_rare_discount"):
                        findings.append({"product": product, "discount": result})
        return findings


async def notify_users(bot: Bot, storage: JsonStorage, findings: list[dict]) -> None:
    users = await storage.get_users()
    for user_id in users:
        for finding in findings:
            product = finding["product"]
            discount = finding["discount"]
            text = (
                f"🔥 Редкая скидка: −{discount['discount_percent']}%\n\n"
                f"{product.title}\n"
                f"Текущая цена: {product.current_price:,.0f} ₽\n"
                f"Средняя за 30 дней: {discount['baseline_price']:,.0f} ₽\n"
                f"Маркетплейс: {product.marketplace}\n"
                f"Категория: {product.category}\n\n"
                f"{product.url}"
            ).replace(",", " ")
            await bot.send_message(user_id, text)
