import logging
from typing import Optional, List

from src.models.users.User import User
from src.config.Database import db

logger = logging.getLogger(__name__)


class UserRepository:
    """Репозиторий для работы с пользователями в PostgreSQL"""

    def __init__(self, database=None):
        self.db = database or db

    async def create_table(self):
        """Создает таблицу пользователей, если она не существует"""
        query = """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            telegram_id BIGINT UNIQUE NOT NULL,
            username VARCHAR(255) DEFAULT '',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);
        CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
        """
        try:
            await self.db.execute(query)
            logger.info("Таблица users создана или уже существует")
        except Exception as e:
            logger.error(f"Ошибка при создании таблицы users: {e}")
            raise

    async def create(self, user: User) -> User:
        """Создает нового пользователя"""
        query = """
        INSERT INTO users (telegram_id, username)
        VALUES ($1, $2)
        RETURNING id, telegram_id, username, created_at
        """
        try:
            row = await self.db.fetchrow(
                query,
                user.telegram_id,
                user.username or ''
            )
            return self._row_to_user(row)
        except Exception as e:
            logger.error(f"Ошибка при создании пользователя: {e}")
            raise

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Получает пользователя по ID"""
        query = """
        SELECT id, telegram_id, username, created_at
        FROM users
        WHERE id = $1
        """
        try:
            row = await self.db.fetchrow(query, user_id)
            return self._row_to_user(row) if row else None
        except Exception as e:
            logger.error(f"Ошибка при получении пользователя по ID {user_id}: {e}")
            raise

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Получает пользователя по Telegram ID"""
        query = """
        SELECT id, telegram_id, username, created_at
        FROM users
        WHERE telegram_id = $1
        """
        try:
            row = await self.db.fetchrow(query, telegram_id)
            return self._row_to_user(row) if row else None
        except Exception as e:
            logger.error(f"Ошибка при получении пользователя по Telegram ID {telegram_id}: {e}")
            raise

    async def get_or_create(self, telegram_id: int, username: str = "") -> tuple[
        User, bool]:
        """
        Получает существующего пользователя или создает нового
        Возвращает кортеж (пользователь, создан_ли_новый)
        """
        user = await self.get_by_telegram_id(telegram_id)
        if user:
            return user, False

        new_user = User(
            telegram_id=telegram_id,
            username=username
        )
        created_user = await self.create(new_user)
        return created_user, True

    async def update(self, user: User) -> Optional[User]:
        """Обновляет данные пользователя"""
        query = """
        UPDATE users
        SET username = $2
        WHERE id = $1
        RETURNING id, telegram_id, username, created_at
        """
        try:
            row = await self.db.fetchrow(
                query,
                user.id,
                user.username or ''
            )
            return self._row_to_user(row) if row else None
        except Exception as e:
            logger.error(f"Ошибка при обновлении пользователя {user.id}: {e}")
            raise

    async def update_by_telegram_id(self, telegram_id: int, username: str = None) -> Optional[User]:
        """Обновляет данные пользователя по Telegram ID"""
        # Сначала получаем текущие данные
        current_user = await self.get_by_telegram_id(telegram_id)
        if not current_user:
            return None

        # Обновляем только переданные поля
        if username is not None:
            current_user.username = username

        return await self.update(current_user)

    async def delete(self, user_id: int) -> bool:
        """Удаляет пользователя по ID"""
        query = "DELETE FROM users WHERE id = $1"
        try:
            result = await self.db.execute(query, user_id)
            return result == "DELETE 1"
        except Exception as e:
            logger.error(f"Ошибка при удалении пользователя {user_id}: {e}")
            raise

    async def delete_by_telegram_id(self, telegram_id: int) -> bool:
        """Удаляет пользователя по Telegram ID"""
        query = "DELETE FROM users WHERE telegram_id = $1"
        try:
            result = await self.db.execute(query, telegram_id)
            return result == "DELETE 1"
        except Exception as e:
            logger.error(f"Ошибка при удалении пользователя по Telegram ID {telegram_id}: {e}")
            raise

    async def get_all(self, limit: int = 100, offset: int = 0) -> List[User]:
        """Получает список всех пользователей с пагинацией"""
        query = """
        SELECT id, telegram_id, username, created_at
        FROM users
        ORDER BY created_at DESC
        LIMIT $1 OFFSET $2
        """
        try:
            rows = await self.db.fetch(query, limit, offset)
            return [self._row_to_user(row) for row in rows]
        except Exception as e:
            logger.error(f"Ошибка при получении списка пользователей: {e}")
            raise

    async def count(self) -> int:
        """Возвращает общее количество пользователей"""
        query = "SELECT COUNT(*) FROM users"
        try:
            return await self.db.fetchval(query)
        except Exception as e:
            logger.error(f"Ошибка при подсчете пользователей: {e}")
            raise

    async def search_by_username(self, username: str) -> List[User]:
        """Ищет пользователей по username (частичное совпадение)"""
        query = """
        SELECT id, telegram_id, username, created_at
        FROM users
        WHERE username ILIKE $1
        ORDER BY username
        LIMIT 50
        """
        try:
            rows = await self.db.fetch(query, f"%{username}%")
            return [self._row_to_user(row) for row in rows]
        except Exception as e:
            logger.error(f"Ошибка при поиске пользователей по username: {e}")
            raise

    async def exists(self, telegram_id: int) -> bool:
        """Проверяет существование пользователя по Telegram ID"""
        query = "SELECT EXISTS(SELECT 1 FROM users WHERE telegram_id = $1)"
        try:
            return await self.db.fetchval(query, telegram_id)
        except Exception as e:
            logger.error(f"Ошибка при проверке существования пользователя: {e}")
            raise

    @staticmethod
    def _row_to_user(row) -> User:
        """Преобразует строку из БД в объект User"""
        if not row:
            return None
        return User(
            id=row['id'],
            telegram_id=row['telegram_id'],
            username=row['username'],
            created_at=row['created_at']
        )
