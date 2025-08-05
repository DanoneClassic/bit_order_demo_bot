import asyncio
import asyncpg
import logging
from typing import Optional
from contextlib import asynccontextmanager
from src.config.DatabaseConfig import DatabaseConfig, db_config

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.pool: Optional[asyncpg.Pool] = None

    async def connect(self):
        """Создает пул соединений с обработкой ошибок"""
        if self.pool is None:
            # Список хостов для попытки подключения
            hosts_to_try = [
                self.config.host,
                'postgres',
                'db',
            ]

            for host in hosts_to_try:
                try:
                    logger.info(f"Попытка подключения к PostgreSQL: {host}:{self.config.port}")

                    # Создаем DSN для текущего хоста
                    dsn = f"postgresql://{self.config.username}:{self.config.password}@{host}:{self.config.port}/{self.config.database}"

                    self.pool = await asyncpg.create_pool(
                        dsn=dsn,
                        min_size=self.config.min_size,
                        max_size=self.config.max_size,
                        max_queries=self.config.max_queries,
                        max_inactive_connection_lifetime=self.config.max_inactive_connection_lifetime,
                        command_timeout=60
                    )

                    # Проверяем соединение
                    async with self.pool.acquire() as connection:
                        version = await connection.fetchval('SELECT version()')
                        logger.info(f"✅ Успешное подключение к PostgreSQL через {host}")
                        logger.info(f"PostgreSQL версия: {version}")
                        return  # Успешно подключились

                except Exception as e:
                    logger.warning(f"❌ Не удалось подключиться к {host}: {e}")
                    if self.pool:
                        await self.pool.close()
                        self.pool = None
                    continue

            # Если все попытки провалились
            raise Exception("Не удалось подключиться ни к одному из хостов PostgreSQL")

    async def disconnect(self):
        """Закрывает пул соединений"""
        if self.pool:
            await self.pool.close()
            self.pool = None
            logger.info("Подключение к базе данных закрыто")

    @asynccontextmanager
    async def get_connection(self):
        """Получает соединение из пула"""
        if not self.pool:
            await self.connect()

        async with self.pool.acquire() as connection:
            yield connection

    async def execute(self, query: str, *args):
        """Выполняет запрос без возврата данных"""
        async with self.get_connection() as conn:
            return await conn.execute(query, *args)

    async def fetch(self, query: str, *args):
        """Выполняет запрос и возвращает все строки"""
        async with self.get_connection() as conn:
            return await conn.fetch(query, *args)

    async def fetchrow(self, query: str, *args):
        """Выполняет запрос и возвращает одну строку"""
        async with self.get_connection() as conn:
            return await conn.fetchrow(query, *args)

    async def fetchval(self, query: str, *args):
        """Выполняет запрос и возвращает одно значение"""
        async with self.get_connection() as conn:
            return await conn.fetchval(query, *args)

    async def executemany(self, query: str, args_list):
        """Выполняет множественные запросы"""
        async with self.get_connection() as conn:
            return await conn.executemany(query, args_list)

    async def wait_for_connection(self, max_attempts: int = 30, delay: int = 2):
        """Ожидает доступности базы данных"""
        for attempt in range(max_attempts):
            try:
                await self.connect()
                logger.info("База данных доступна")
                return True
            except Exception as e:
                logger.warning(f"Попытка подключения {attempt + 1}/{max_attempts} неудачна: {e}")
                if attempt < max_attempts - 1:
                    await asyncio.sleep(delay)

        logger.error(f"Не удалось подключиться к базе данных за {max_attempts} попыток")
        return False

    async def health_check(self):
        """Проверка здоровья базы данных"""
        try:
            async with self.get_connection() as conn:
                await conn.fetchval('SELECT 1')
            return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False


# Глобальный экземпляр
db = Database(db_config)