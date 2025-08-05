import logging
from decimal import Decimal
from typing import List, Optional

from src.config.Database import db
from src.models.users.Master import Master
from src.models.Service import Service

logger = logging.getLogger(__name__)


class MasterRepository():
    """Репозиторий для работы с мастерами в PostgreSQL"""

    def __init__(self, database=None):
        self.db = database or db

    async def create_table(self):
        """Создает таблицы мастеров и связей с услугами"""
        query = """
        CREATE TABLE IF NOT EXISTS masters (
            id SERIAL PRIMARY KEY,
            telegram_id BIGINT UNIQUE,
            username VARCHAR(255) DEFAULT '',
            name VARCHAR(255),
            phone VARCHAR(20),
            email VARCHAR(255),
            specialization VARCHAR(255),
            experience_years INTEGER DEFAULT 0,
            rating DECIMAL(3,2) DEFAULT 0.00,
            is_active BOOLEAN DEFAULT TRUE,
            working_hours_start TIME,
            working_hours_end TIME,
            working_days VARCHAR(20),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS master_services (
            id SERIAL PRIMARY KEY,
            master_id INTEGER REFERENCES masters(id) ON DELETE CASCADE,
            service_id INTEGER REFERENCES services(id) ON DELETE CASCADE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(master_id, service_id)
        );

        CREATE INDEX IF NOT EXISTS idx_masters_telegram_id ON masters(telegram_id);
        CREATE INDEX IF NOT EXISTS idx_masters_is_active ON masters(is_active);
        CREATE INDEX IF NOT EXISTS idx_masters_specialization ON masters(specialization);
        CREATE INDEX IF NOT EXISTS idx_master_services_master_id ON master_services(master_id);
        CREATE INDEX IF NOT EXISTS idx_master_services_service_id ON master_services(service_id);

        -- Триггер для автоматического обновления updated_at
        DROP TRIGGER IF EXISTS update_masters_updated_at ON masters;
        CREATE TRIGGER update_masters_updated_at
            BEFORE UPDATE ON masters
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        """
        try:
            await self.db.execute(query)
            logger.info("Таблицы masters и master_services созданы или уже существуют")
        except Exception as e:
            logger.error(f"Ошибка при создании таблиц мастеров: {e}")
            raise

    async def create(self, master: Master) -> Master:
        """Создает нового мастера"""
        query = """
        INSERT INTO masters (telegram_id, username, name, phone, email, specialization, 
                           experience_years, rating, is_active, working_hours_start, 
                           working_hours_end, working_days)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
        RETURNING id, telegram_id, username, name, phone, email, specialization, 
                 experience_years, rating, is_active, working_hours_start, 
                 working_hours_end, working_days, created_at, updated_at
        """
        try:
            row = await self.db.fetchrow(
                query,
                master.telegram_id,
                master.username,
                master.name,
                master.phone,
                master.email,
                master.specialization,
                master.experience_years,
                master.rating,
                master.is_active,
                master.working_hours_start,
                master.working_hours_end,
                master.working_days
            )
            created_master = self._row_to_master(row)

            # Добавляем услуги мастеру
            if master.service_ids:
                for service_id in master.service_ids:
                    await self.add_service_to_master(created_master.id, service_id)
                created_master.service_ids = master.service_ids

            return created_master
        except Exception as e:
            logger.error(f"Ошибка при создании мастера: {e}")
            raise

    async def get_by_id(self, master_id: int) -> Optional[Master]:
        """Получает мастера по ID"""
        query = """
        SELECT id, telegram_id, username, name, phone, email, specialization, 
               experience_years, rating, is_active, working_hours_start, 
               working_hours_end, working_days, created_at, updated_at
        FROM masters
        WHERE id = $1
        """
        try:
            row = await self.db.fetchrow(query, master_id)
            if not row:
                return None

            master = self._row_to_master(row)
            # Получаем услуги мастера
            service_ids = await self._get_master_service_ids(master_id)
            master.service_ids = service_ids
            return master
        except Exception as e:
            logger.error(f"Ошибка при получении мастера по ID {master_id}: {e}")
            raise

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[Master]:
        """Получает мастера по Telegram ID"""
        query = """
        SELECT id, telegram_id, username, name, phone, email, specialization, 
               experience_years, rating, is_active, working_hours_start, 
               working_hours_end, working_days, created_at, updated_at
        FROM masters
        WHERE telegram_id = $1
        """
        try:
            row = await self.db.fetchrow(query, telegram_id)
            if not row:
                return None

            master = self._row_to_master(row)
            service_ids = await self._get_master_service_ids(master.id)
            master.service_ids = service_ids
            return master
        except Exception as e:
            logger.error(f"Ошибка при получении мастера по Telegram ID {telegram_id}: {e}")
            raise

    async def get_all(self) -> List[Master]:
        """Получает всех мастеров"""
        query = """
        SELECT id, telegram_id, username, name, phone, email, specialization, 
               experience_years, rating, is_active, working_hours_start, 
               working_hours_end, working_days, created_at, updated_at
        FROM masters
        ORDER BY name
        """
        try:
            rows = await self.db.fetch(query)
            masters = []
            for row in rows:
                master = self._row_to_master(row)
                service_ids = await self._get_master_service_ids(master.id)
                master.service_ids = service_ids
                masters.append(master)
            return masters
        except Exception as e:
            logger.error(f"Ошибка при получении всех мастеров: {e}")
            raise

    async def get_active_masters(self) -> List[Master]:
        """Получает только активных мастеров"""
        query = """
        SELECT id, telegram_id, username, name, phone, email, specialization, 
               experience_years, rating, is_active, working_hours_start, 
               working_hours_end, working_days, created_at, updated_at
        FROM masters
        WHERE is_active = TRUE
        ORDER BY rating DESC, name
        """
        try:
            rows = await self.db.fetch(query)
            masters = []
            for row in rows:
                master = self._row_to_master(row)
                service_ids = await self._get_master_service_ids(master.id)
                master.service_ids = service_ids
                masters.append(master)
            return masters
        except Exception as e:
            logger.error(f"Ошибка при получении активных мастеров: {e}")
            raise

    async def get_by_service(self, service_id: int) -> List[Master]:
        """Получает мастеров, оказывающих определённую услугу"""
        query = """
        SELECT m.id, m.telegram_id, m.username, m.name, m.phone, m.email, m.specialization, 
               m.experience_years, m.rating, m.is_active, m.working_hours_start, 
               m.working_hours_end, m.working_days, m.created_at, m.updated_at
        FROM masters m
        INNER JOIN master_services ms ON m.id = ms.master_id
        WHERE ms.service_id = $1 AND m.is_active = TRUE
        ORDER BY m.rating DESC, m.name
        """
        try:
            rows = await self.db.fetch(query, service_id)
            masters = []
            for row in rows:
                master = self._row_to_master(row)
                service_ids = await self._get_master_service_ids(master.id)
                master.service_ids = service_ids
                masters.append(master)
            return masters
        except Exception as e:
            logger.error(f"Ошибка при получении мастеров по услуге {service_id}: {e}")
            raise

    async def get_by_specialization(self, specialization: str) -> List[Master]:
        """Получает мастеров по специализации"""
        query = """
        SELECT id, telegram_id, username, name, phone, email, specialization, 
               experience_years, rating, is_active, working_hours_start, 
               working_hours_end, working_days, created_at, updated_at
        FROM masters
        WHERE specialization ILIKE $1 AND is_active = TRUE
        ORDER BY rating DESC, experience_years DESC
        """
        try:
            rows = await self.db.fetch(query, f"%{specialization}%")
            masters = []
            for row in rows:
                master = self._row_to_master(row)
                service_ids = await self._get_master_service_ids(master.id)
                master.service_ids = service_ids
                masters.append(master)
            return masters
        except Exception as e:
            logger.error(f"Ошибка при получении мастеров по специализации {specialization}: {e}")
            raise

    async def update(self, master: Master) -> Master:
        """Обновляет данные мастера"""
        query = """
        UPDATE masters 
        SET telegram_id = $2, username = $3, name = $4, phone = $5, email = $6,
            specialization = $7, experience_years = $8, rating = $9, is_active = $10,
            working_hours_start = $11, working_hours_end = $12, working_days = $13
        WHERE id = $1
        RETURNING id, telegram_id, username, name, phone, email, specialization, 
                 experience_years, rating, is_active, working_hours_start, 
                 working_hours_end, working_days, created_at, updated_at
        """
        try:
            row = await self.db.fetchrow(
                query,
                master.id,
                master.telegram_id,
                master.username,
                master.name,
                master.phone,
                master.email,
                master.specialization,
                master.experience_years,
                master.rating,
                master.is_active,
                master.working_hours_start,
                master.working_hours_end,
                master.working_days
            )
            return self._row_to_master(row) if row else master
        except Exception as e:
            logger.error(f"Ошибка при обновлении мастера {master.id}: {e}")
            raise

    async def delete(self, master_id: int) -> bool:
        """Удаляет мастера (мягкое удаление)"""
        query = "UPDATE masters SET is_active = FALSE WHERE id = $1"
        try:
            result = await self.db.execute(query, master_id)
            return result == "UPDATE 1"
        except Exception as e:
            logger.error(f"Ошибка при удалении мастера {master_id}: {e}")
            raise

    async def add_service_to_master(self, master_id: int, service_id: int) -> bool:
        """Добавляет услугу мастеру"""
        query = """
        INSERT INTO master_services (master_id, service_id)
        VALUES ($1, $2)
        ON CONFLICT (master_id, service_id) DO NOTHING
        """
        try:
            await self.db.execute(query, master_id, service_id)
            return True
        except Exception as e:
            logger.error(f"Ошибка при добавлении услуги {service_id} мастеру {master_id}: {e}")
            raise

    async def remove_service_from_master(self, master_id: int, service_id: int) -> bool:
        """Убирает услугу у мастера"""
        query = "DELETE FROM master_services WHERE master_id = $1 AND service_id = $2"
        try:
            result = await self.db.execute(query, master_id, service_id)
            return result == "DELETE 1"
        except Exception as e:
            logger.error(f"Ошибка при удалении услуги {service_id} у мастера {master_id}: {e}")
            raise

    async def get_master_services(self, master_id: int) -> List[Service]:
        """Получает все услуги мастера"""
        query = """
        SELECT s.id, s.name, s.description, s.category, s.subcategory, s.price, 
               s.duration_minutes, s.is_active, s.created_at, s.updated_at
        FROM services s
        INNER JOIN master_services ms ON s.id = ms.service_id
        WHERE ms.master_id = $1 AND s.is_active = TRUE
        ORDER BY s.category, s.name
        """
        try:
            rows = await self.db.fetch(query, master_id)
            return [self._row_to_service(row) for row in rows]
        except Exception as e:
            logger.error(f"Ошибка при получении услуг мастера {master_id}: {e}")
            raise

    async def _get_master_service_ids(self, master_id: int) -> List[int]:
        """Получает ID услуг мастера"""
        query = "SELECT service_id FROM master_services WHERE master_id = $1"
        try:
            rows = await self.db.fetch(query, master_id)
            return [row['service_id'] for row in rows]
        except Exception as e:
            logger.error(f"Ошибка при получении ID услуг мастера {master_id}: {e}")
            return []

    def _row_to_master(self, row) -> Master:
        """Преобразует строку БД в объект Master"""
        return Master(
            id=row['id'],
            telegram_id=row['telegram_id'],
            username=row['username'],
            name=row['name'],
            phone=row['phone'],
            email=row['email'],
            specialization=row['specialization'],
            experience_years=row['experience_years'],
            rating=float(row['rating']) if row['rating'] else 0.0,
            is_active=row['is_active'],
            working_hours_start=row['working_hours_start'].strftime('%H:%M') if row['working_hours_start'] else None,
            working_hours_end=row['working_hours_end'].strftime('%H:%M') if row['working_hours_end'] else None,
            working_days=row['working_days'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )

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