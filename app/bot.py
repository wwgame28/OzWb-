import asyncio
import logging

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.collectors import DemoCollector, OzonCollector, WildberriesCollector
from app.config import get_settings
from app.scanner import Scanner, notify_users
from app.json_storage import JsonStorage

router = Router()
settings = get_settings()
storage = JsonStorage(settings.database_path)
collectors = [DemoCollector(), OzonCollector(), WildberriesCollector()]
scanner = Scanner(
    storage=storage,
    collectors=collectors,
    threshold=settings.rare_discount_threshold,
    min_points=settings.min_history_points,
)


@router.message(Command("start"))
async def start(message: Message) -> None:
    await storage.add_user(message.from_user.id)
    await message.answer(
        "Привет! Я мониторю категории Ozon/WB и ищу редкие скидки по истории цен.\n\n"
        "Команды:\n"
        "/categories — категории мониторинга\n"
        "/scan — ручной запуск проверки"
    )


@router.message(Command("categories"))
async def categories(message: Message) -> None:
    await message.answer("Категории: " + ", ".join(settings.categories))


@router.message(Command("scan"))
async def scan(message: Message, bot: Bot) -> None:
    await message.answer("Запускаю сканирование категорий...")
    findings = await scanner.scan(settings.categories)
    if not findings:
        await message.answer("Редких скидок пока не найдено. История цен будет точнее после нескольких запусков.")
        return
    await notify_users(bot, storage, findings)


async def scheduled_scan(bot: Bot) -> None:
    findings = await scanner.scan(settings.categories)
    if findings:
        await notify_users(bot, storage, findings)


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    await storage.init()

    bot = Bot(token=settings.telegram_bot_token)
    dp = Dispatcher()
    dp.include_router(router)

    scheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.add_job(
        scheduled_scan,
        "interval",
        hours=settings.scan_interval_hours,
        args=[bot],
        max_instances=1,
    )
    scheduler.start()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
