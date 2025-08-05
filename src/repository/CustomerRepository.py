
import logging
from typing import Optional, List
from datetime import datetime

from src.config.Database import db
from src.models.users.Customer import Customer

logger = logging.getLogger(__name__)


class CustomerRepository:
    """Репозиторий для работы с клиентами в PostgreSQL"""

    def __init__(self, database=None):
        self.db = database or db

    async def create_table(self):
        """Создает таблицу клиентов"""
        query = """
        CREATE TABLE IF NOT EXISTS customers (
            id SERIAL PRIMARY KEY,
            telegram_id BIGINT UNIQUE,
            username VARCHAR(255) DEFAULT '',
            name VARCHAR(255),
            address TEXT,
            phone VARCHAR(20),
            email VARCHAR(255),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_customers_telegram_id ON customers(telegram_id);

        -- Триггер для автоматического обновления updated_at
        DROP TRIGGER IF EXISTS update_customers_updated_at ON customers;
        CREATE TRIGGER update_customers_updated_at
            BEFORE UPDATE ON customers
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        """
        try:
            await self.db.execute(query)
            logger.info("Таблица customers создана или уже существует")
        except Exception as e:
            logger.error(f"Ошибка при создании таблицы customers: {e}")
            raise

    async def create(self, customer: Customer) -> Customer:
        """Создает нового клиента"""
        query = """
        INSERT INTO customers (telegram_id, username, name, address, phone, email)
        VALUES ($1, $2, $3, $4, $5, $6)
        RETURNING id, telegram_id, username, name, address, phone, email, created_at, updated_at
        """
        try:
            row = await self.db.fetchrow(
                query,
                customer.telegram_id,
                customer.username,
                customer.name,
                customer.address,
                customer.phone,
                customer.email
            )
            return self._row_to_customer(row)
        except Exception as e:
            logger.error(f"Ошибка при создании клиента: {e}")
            raise

    async def get_by_id(self, customer_id: int) -> Optional[Customer]:
        """Получает клиента по ID"""
        query = """
        SELECT id, telegram_id, username, name, address, phone, email, created_at, updated_at
        FROM customers
        WHERE id = $1
        """
        try:
            row = await self.db.fetchrow(query, customer_id)
            return self._row_to_customer(row) if row else None
        except Exception as e:
            logger.error(f"Ошибка при получении клиента по ID {customer_id}: {e}")
            raise

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[Customer]:
        """Получает клиента по Telegram ID"""
        query = """
        SELECT id, telegram_id, username, name, address, phone, email, created_at, updated_at
        FROM customers
        WHERE telegram_id = $1
        """
        try:
            row = await self.db.fetchrow(query, telegram_id)
            return self._row_to_customer(row) if row else None
        except Exception as e:
            logger.error(f"Ошибка при получении клиента по Telegram ID {telegram_id}: {e}")
            raise

    async def get_all(self) -> List[Customer]:
        """Получает всех клиентов"""
        query = """
        SELECT id, telegram_id, username, name, address, phone, email, created_at, updated_at
        FROM customers
        ORDER BY created_at DESC
        """
        try:
            rows = await self.db.fetch(query)
            return [self._row_to_customer(row) for row in rows]
        except Exception as e:
            logger.error(f"Ошибка при получении всех клиентов: {e}")
            raise

    async def update(self, customer: Customer) -> Customer:
        """Обновляет данные клиента"""
        query = """
        UPDATE customers 
        SET telegram_id = $2, username = $3, name = $4, address = $5, phone = $6, email = $7
        WHERE id = $1
        RETURNING id, telegram_id, username, name, address, phone, email, created_at, updated_at
        """
        try:
            row = await self.db.fetchrow(
                query,
                customer.id,
                customer.telegram_id,
                customer.username,
                customer.name,
                customer.address,
                customer.phone,
                customer.email
            )
            return self._row_to_customer(row) if row else customer
        except Exception as e:
            logger.error(f"Ошибка при обновлении клиента {customer.id}: {e}")
            raise

    async def delete(self, customer_id: int) -> bool:
        """Удаляет клиента по ID"""
        query = "DELETE FROM customers WHERE id = $1"
        try:
            result = await self.db.execute(query, customer_id)
            return result == "DELETE 1"
        except Exception as e:
            logger.error(f"Ошибка при удалении клиента {customer_id}: {e}")
            raise

    def _row_to_customer(self, row) -> Customer:
        """Преобразует строку БД в объект Customer"""
        if row is None:
            return None

        return Customer(
            id=row['id'],
            telegram_id=row['telegram_id'],
            username=row['username'],
            name=row['name'],
            address=row['address'],
            phone=row['phone'],
            email=row['email'],
            created_at=row['created_at']
        )
