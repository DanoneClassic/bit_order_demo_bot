import os
from typing import Optional
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv

class BotSingleton:
    _instance: Optional['BotSingleton'] = None
    _bot: Optional[Bot] = None

    def __new__(cls) -> 'BotSingleton':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # Инициализируем только один раз
        if self._bot is None:
            load_dotenv()
            token = os.getenv("BOT_TOKEN")
            if not token:
                raise ValueError("BOT_TOKEN не найден в переменных окружения")

            self._bot = Bot(
                token=token,
                default=DefaultBotProperties(parse_mode=ParseMode.HTML)
            )

    @property
    def bot(self) -> Bot:
        """Возвращает экземпляр бота"""
        if self._bot is None:
            raise RuntimeError("Бот не инициализирован")
        return self._bot

    async def close(self):
        """Закрывает сессию бота"""
        if self._bot:
            await self._bot.session.close()
            self._bot = None

    @classmethod
    def get_bot(cls) -> Bot:
        """Статический метод для получения бота"""
        instance = cls()
        return instance.bot


bot_instance = BotSingleton()