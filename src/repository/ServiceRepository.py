import logging
from typing import List, Optional
from decimal import Decimal

from src.config.Database import db
from src.models.Service import Service

logger = logging.getLogger(__name__)


class ServiceRepository:
    """Репозиторий для работы с услугами в PostgreSQL"""

    def __init__(self, database=None):
        self.db = database or db

    async def create_table(self):
        """Создает таблицу услуг, если она не существует"""
        query = """
        CREATE TABLE IF NOT EXISTS services (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            category VARCHAR(100) NOT NULL,
            subcategory VARCHAR(100),
            price DECIMAL(10,2) NOT NULL DEFAULT 0.00,
            duration_minutes INTEGER NOT NULL DEFAULT 0,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_services_category ON services(category);
        CREATE INDEX IF NOT EXISTS idx_services_is_active ON services(is_active);
        CREATE INDEX IF NOT EXISTS idx_services_name ON services(name);

        -- Триггер для автоматического обновления updated_at
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';

        DROP TRIGGER IF EXISTS update_services_updated_at ON services;
        CREATE TRIGGER update_services_updated_at
            BEFORE UPDATE ON services
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        """
        try:
            await self.db.execute(query)
            logger.info("Таблица services создана или уже существует")
        except Exception as e:
            logger.error(f"Ошибка при создании таблицы services: {e}")
            raise

    async def create(self, service: Service) -> Service:
        """Создает новую услугу"""
        query = """
        INSERT INTO services (name, description, category, subcategory, price, duration_minutes, is_active)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        RETURNING id, name, description, category, subcategory, price, duration_minutes, is_active, created_at, updated_at
        """
        try:
            row = await self.db.fetchrow(
                query,
                service.name,
                service.description,
                service.category,
                service.subcategory,
                service.price,
                service.duration_minutes,
                service.is_active
            )
            return self._row_to_service(row)
        except Exception as e:
            logger.error(f"Ошибка при создании услуги: {e}")
            raise

    async def get_by_id(self, service_id: int) -> Optional[Service]:
        """Получает услугу по ID"""
        query = """
        SELECT id, name, description, category, subcategory, price, duration_minutes, is_active, created_at, updated_at
        FROM services
        WHERE id = $1
        """
        try:
            row = await self.db.fetchrow(query, service_id)
            return self._row_to_service(row) if row else None
        except Exception as e:
            logger.error(f"Ошибка при получении услуги по ID {service_id}: {e}")
            raise

    async def get_all(self) -> List[Service]:
        """Получает все услуги"""
        query = """
        SELECT id, name, description, category, subcategory, price, duration_minutes, is_active, created_at, updated_at
        FROM services
        ORDER BY category, name
        """
        try:
            rows = await self.db.fetch(query)
            return [self._row_to_service(row) for row in rows]
        except Exception as e:
            logger.error(f"Ошибка при получении всех услуг: {e}")
            raise

    async def get_by_category(self, category: str) -> List[Service]:
        """Получает услуги по категории"""
        query = """
        SELECT id, name, description, category, subcategory, price, duration_minutes, is_active, created_at, updated_at
        FROM services
        WHERE category = $1 AND is_active = TRUE
        ORDER BY name
        """
        try:
            rows = await self.db.fetch(query, category)
            return [self._row_to_service(row) for row in rows]
        except Exception as e:
            logger.error(f"Ошибка при получении услуг по категории {category}: {e}")
            raise

    async def get_by_name(self, service: str) -> List[Service]:
        """Получает услуги по категории"""
        query = """
        SELECT id, name, description, category, subcategory, price, duration_minutes, is_active, created_at, updated_at
        FROM services
        WHERE name = $1 
        """
        try:
            row = await self.db.fetchrow(query, service)
            return self._row_to_service(row) if row else None
        except Exception as e:
            logger.error(f"Ошибка при получении услуг по категории {service}: {e}")
            raise

    async def get_active_services(self) -> List[Service]:
        """Получает только активные услуги"""
        query = """
        SELECT id, name, description, category, subcategory, price, duration_minutes, is_active, created_at, updated_at
        FROM services
        WHERE is_active = TRUE
        ORDER BY category, name
        """
        try:
            rows = await self.db.fetch(query)
            return [self._row_to_service(row) for row in rows]
        except Exception as e:
            logger.error(f"Ошибка при получении активных услуг: {e}")
            raise

    async def update(self, service: Service) -> Service:
        """Обновляет услугу"""
        query = """
        UPDATE services 
        SET name = $2, description = $3, category = $4, subcategory = $5, 
            price = $6, duration_minutes = $7, is_active = $8
        WHERE id = $1
        RETURNING id, name, description, category, subcategory, price, duration_minutes, is_active, created_at, updated_at
        """
        try:
            row = await self.db.fetchrow(
                query,
                service.id,
                service.name,
                service.description,
                service.category,
                service.subcategory,
                service.price,
                service.duration_minutes,
                service.is_active
            )
            return self._row_to_service(row) if row else service
        except Exception as e:
            logger.error(f"Ошибка при обновлении услуги {service.id}: {e}")
            raise

    async def delete(self, service_id: int) -> bool:
        """Удаляет услугу (мягкое удаление)"""
        query = "UPDATE services SET is_active = FALSE WHERE id = $1"
        try:
            result = await self.db.execute(query, service_id)
            return result == "UPDATE 1"
        except Exception as e:
            logger.error(f"Ошибка при удалении услуги {service_id}: {e}")
            raise

    async def search_by_description(self, description: str) -> List[Service]:
        """Поиск услуг по описанию"""
        query = """
        SELECT id, name, description, category, subcategory, price, duration_minutes, is_active, created_at, updated_at
        FROM services
        WHERE description ILIKE $1 AND is_active = TRUE
        ORDER BY name
        """
        try:
            rows = await self.db.fetch(query, f"%{description}%")
            return [self._row_to_service(row) for row in rows]
        except Exception as e:
            logger.error(f"Ошибка при поиске услуг по описанию {description}: {e}")
            raise

    async def search_by_name(self, name: str) -> List[Service]:
        """Поиск услуг по названию"""
        query = """
        SELECT id, name, description, category, subcategory, price, duration_minutes, is_active, created_at, updated_at
        FROM services
        WHERE name ILIKE $2
        ORDER BY name
        """
        try:
            rows = await self.db.fetch(query, f"%{name}%")
            return [self._row_to_service(row) for row in rows]
        except Exception as e:
            logger.error(f"Ошибка при поиске услуг по названию {name}: {e}")
            raise
    #
    # async def search_by_name(self, name: str) -> Optional[Service]:
    #     """Ищет услугу по имени"""
    #     query = """
    #     SELECT id, name, description, category, subcategory, price,
    #            duration_minutes, is_active, created_at, updated_at
    #     FROM services
    #     WHERE name = $1
    #     """
    #     try:
    #         # Передаем аргумент в виде кортежа или списка
    #         row = await self.db.fetchrow(query, name)
    #         if row:
    #             return self._row_to_service(row)
    #         return None
    #     except Exception as e:
    #         logger.error(f"Ошибка при поиске услуг по названию {name}: {e}")
    #         raise

    async def get_by_price_range(self, min_price: float, max_price: float) -> List[Service]:
        """Получает услуги в диапазоне цен"""
        query = """
        SELECT id, name, description, category, subcategory, price, duration_minutes, is_active, created_at, updated_at
        FROM services
        WHERE price BETWEEN $1 AND $2 AND is_active = TRUE
        ORDER BY price
        """
        try:
            rows = await self.db.fetch(query, min_price, max_price)
            return [self._row_to_service(row) for row in rows]
        except Exception as e:
            logger.error(f"Ошибка при получении услуг в диапазоне цен {min_price}-{max_price}: {e}")
            raise

    def _row_to_service(self, row) -> Service:
        """Преобразует строку БД в объект Service"""
        return Service(
            id=row['id'],
            name=row['name'],
            description=row['description'],
            category=row['category'],
            subcategory=row['subcategory'],
            price=Decimal(str(row['price'])),
            duration_minutes=row['duration_minutes'],
            is_active=row['is_active'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )

