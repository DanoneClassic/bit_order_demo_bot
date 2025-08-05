import logging
from decimal import Decimal
from typing import List, Optional
from datetime import datetime, date, timedelta

from src.config.Database import db
from src.models.Order import Order, OrderStatus

logger = logging.getLogger(__name__)


class OrderRepository:
    """Репозиторий для работы с заказами в PostgreSQL"""

    def __init__(self, database=None):
        self.db = database or db

    async def create_table(self):
        """Создает таблицу заказов"""
        query = """
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            master_id INTEGER NOT NULL REFERENCES masters(id) ON DELETE CASCADE,
            service_id INTEGER NOT NULL REFERENCES services(id) ON DELETE CASCADE,
            appointment_datetime TIMESTAMP WITH TIME ZONE NOT NULL,
            duration_minutes INTEGER NOT NULL DEFAULT 0,
            total_price DECIMAL(10,2) NOT NULL DEFAULT 0.00,
            status VARCHAR(20) NOT NULL DEFAULT 'pending',
            notes TEXT,
            client_name VARCHAR(255),
            client_phone VARCHAR(20),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
        CREATE INDEX IF NOT EXISTS idx_orders_master_id ON orders(master_id);
        CREATE INDEX IF NOT EXISTS idx_orders_service_id ON orders(service_id);
        CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
        CREATE INDEX IF NOT EXISTS idx_orders_appointment_datetime ON orders(appointment_datetime);
        CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at);

        -- Триггер для автоматического обновления updated_at
        DROP TRIGGER IF EXISTS update_orders_updated_at ON orders;
        CREATE TRIGGER update_orders_updated_at
            BEFORE UPDATE ON orders
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        """
        try:
            await self.db.execute(query)
            logger.info("Таблица orders создана или уже существует")
        except Exception as e:
            logger.error(f"Ошибка при создании таблицы orders: {e}")
            raise

    async def create(self, order: Order) -> Order:
        """Создает новый заказ"""
        query = """
        INSERT INTO orders (user_id, master_id, service_id, appointment_datetime, 
                          duration_minutes, total_price, status, notes, client_name, client_phone)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        RETURNING id, user_id, master_id, service_id, appointment_datetime, duration_minutes,
                 total_price, status, notes, client_name, client_phone, created_at, updated_at
        """
        try:
            row = await self.db.fetchrow(
                query,
                order.user_id,
                order.master_id,
                order.service_id,
                order.appointment_datetime,
                order.duration_minutes,
                order.total_price,
                order.status.value,
                order.notes,
                order.client_name,
                order.client_phone
            )
            return self._row_to_order(row)
        except Exception as e:
            logger.error(f"Ошибка при создании заказа: {e}")
            raise

    async def get_by_id(self, order_id: int) -> Optional[Order]:
        """Получает заказ по ID"""
        query = """
        SELECT id, user_id, master_id, service_id, appointment_datetime, duration_minutes,
               total_price, status, notes, client_name, client_phone, created_at, updated_at
        FROM orders
        WHERE id = $1
        """
        try:
            row = await self.db.fetchrow(query, order_id)
            return self._row_to_order(row) if row else None
        except Exception as e:
            logger.error(f"Ошибка при получении заказа по ID {order_id}: {e}")
            raise

    async def get_all(self) -> List[Order]:
        """Получает все заказы"""
        query = """
        SELECT id, user_id, master_id, service_id, appointment_datetime, duration_minutes,
               total_price, status, notes, client_name, client_phone, created_at, updated_at
        FROM orders
        ORDER BY appointment_datetime DESC
        """
        try:
            rows = await self.db.fetch(query)
            return [self._row_to_order(row) for row in rows]
        except Exception as e:
            logger.error(f"Ошибка при получении всех заказов: {e}")
            raise

    async def get_by_user_id(self, user_id: int) -> List[Order]:
        """Получает заказы пользователя"""
        query = """
        SELECT id, user_id, master_id, service_id, appointment_datetime, duration_minutes,
               total_price, status, notes, client_name, client_phone, created_at, updated_at
        FROM orders
        WHERE user_id = $1
        ORDER BY appointment_datetime DESC
        """
        try:
            rows = await self.db.fetch(query, user_id)
            return [self._row_to_order(row) for row in rows]
        except Exception as e:
            logger.error(f"Ошибка при получении заказов пользователя {user_id}: {e}")
            raise

    async def get_by_master_id(self, master_id: int) -> List[Order]:
        """Получает заказы мастера"""
        query = """
        SELECT id, user_id, master_id, service_id, appointment_datetime, duration_minutes,
               total_price, status, notes, client_name, client_phone, created_at, updated_at
        FROM orders
        WHERE master_id = $1
        ORDER BY appointment_datetime DESC
        """
        try:
            rows = await self.db.fetch(query, master_id)
            return [self._row_to_order(row) for row in rows]
        except Exception as e:
            logger.error(f"Ошибка при получении заказов мастера {master_id}: {e}")
            raise

    async def get_by_status(self, status: OrderStatus) -> List[Order]:
        """Получает заказы по статусу"""
        query = """
        SELECT id, user_id, master_id, service_id, appointment_datetime, duration_minutes,
               total_price, status, notes, client_name, client_phone, created_at, updated_at
        FROM orders
        WHERE status = $1
        ORDER BY appointment_datetime
        """
        try:
            rows = await self.db.fetch(query, status.value)
            return [self._row_to_order(row) for row in rows]
        except Exception as e:
            logger.error(f"Ошибка при получении заказов по статусу {status.value}: {e}")
            raise

    async def get_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Order]:
        """Получает заказы в диапазоне дат"""
        query = """
        SELECT id, user_id, master_id, service_id, appointment_datetime, duration_minutes,
               total_price, status, notes, client_name, client_phone, created_at, updated_at
        FROM orders
        WHERE appointment_datetime >= $1 AND appointment_datetime <= $2
        ORDER BY appointment_datetime
        """
        try:
            rows = await self.db.fetch(query, start_date, end_date)
            return [self._row_to_order(row) for row in rows]
        except Exception as e:
            logger.error(f"Ошибка при получении заказов в диапазоне дат {start_date} - {end_date}: {e}")
            raise

    async def get_today_orders(self) -> List[Order]:
        """Получает заказы на сегодня"""
        today = date.today()
        start_of_day = datetime.combine(today, datetime.min.time())
        end_of_day = datetime.combine(today, datetime.max.time())

        return await self.get_by_date_range(start_of_day, end_of_day)

    async def get_upcoming_orders(self, user_id: int) -> List[Order]:
        """Получает предстоящие заказы пользователя"""
        query = """
        SELECT id, user_id, master_id, service_id, appointment_datetime, duration_minutes,
               total_price, status, notes, client_name, client_phone, created_at, updated_at
        FROM orders
        WHERE user_id = $1 
        AND appointment_datetime > CURRENT_TIMESTAMP
        AND status IN ('pending', 'confirmed')
        ORDER BY appointment_datetime
        """
        try:
            rows = await self.db.fetch(query, user_id)
            return [self._row_to_order(row) for row in rows]
        except Exception as e:
            logger.error(f"Ошибка при получении предстоящих заказов пользователя {user_id}: {e}")
            raise

    async def update(self, order: Order) -> Order:
        """Обновляет заказ"""
        query = """
        UPDATE orders 
        SET user_id = $2, master_id = $3, service_id = $4, appointment_datetime = $5,
            duration_minutes = $6, total_price = $7, status = $8, notes = $9,
            client_name = $10, client_phone = $11
        WHERE id = $1
        RETURNING id, user_id, master_id, service_id, appointment_datetime, duration_minutes,
                 total_price, status, notes, client_name, client_phone, created_at, updated_at
        """
        try:
            row = await self.db.fetchrow(
                query,
                order.id,
                order.user_id,
                order.master_id,
                order.service_id,
                order.appointment_datetime,
                order.duration_minutes,
                order.total_price,
                order.status.value,
                order.notes,
                order.client_name,
                order.client_phone
            )
            return self._row_to_order(row) if row else order
        except Exception as e:
            logger.error(f"Ошибка при обновлении заказа {order.id}: {e}")
            raise

    async def update_status(self, order_id: int, status: OrderStatus) -> bool:
        """Обновляет статус заказа"""
        query = "UPDATE orders SET status = $2 WHERE id = $1"
        try:
            result = await self.db.execute(query, order_id, status.value)
            return result == "UPDATE 1"
        except Exception as e:
            logger.error(f"Ошибка при обновлении статуса заказа {order_id}: {e}")
            raise

    async def delete(self, order_id: int) -> bool:
        """Удаляет заказ"""
        query = "DELETE FROM orders WHERE id = $1"
        try:
            result = await self.db.execute(query, order_id)
            return result == "DELETE 1"
        except Exception as e:
            logger.error(f"Ошибка при удалении заказа {order_id}: {e}")
            raise

    async def check_master_availability(
            self,
            master_id: int,
            appointment_datetime: datetime,
            duration_minutes: int,
            exclude_order_id: int = None
    ) -> bool:
        """Проверяет доступность мастера в указанное время"""
        end_time = appointment_datetime + timedelta(minutes=duration_minutes)

        # Базовый запрос для проверки пересечений
        query = """
        SELECT COUNT(*) as conflicts
        FROM orders
        WHERE master_id = $1
        AND status NOT IN ('cancelled', 'no_show')
        AND (
            -- Новое время начинается во время существующей записи
            (appointment_datetime <= $2 AND appointment_datetime + INTERVAL '1 minute' * duration_minutes > $2)
            OR
            -- Новое время заканчивается во время существующей записи
            (appointment_datetime < $3 AND appointment_datetime + INTERVAL '1 minute' * duration_minutes >= $3)
            OR
            -- Новое время полностью охватывает существующую запись
            (appointment_datetime >= $2 AND appointment_datetime + INTERVAL '1 minute' * duration_minutes <= $3)
        )
        """

        params = [master_id, appointment_datetime, end_time]

        # Исключаем текущий заказ при обновлении
        if exclude_order_id:
            query += " AND id != $4"
            params.append(exclude_order_id)

        try:
            row = await self.db.fetchrow(query, *params)
            return row['conflicts'] == 0
        except Exception as e:
            logger.error(f"Ошибка при проверке доступности мастера {master_id}: {e}")
            raise

    async def get_master_schedule(self, master_id: int, date: datetime) -> List[Order]:
        """Получает расписание мастера на день"""
        start_of_day = datetime.combine(date.date(), datetime.min.time())
        end_of_day = datetime.combine(date.date(), datetime.max.time())

        query = """
        SELECT id, user_id, master_id, service_id, appointment_datetime, duration_minutes,
               total_price, status, notes, client_name, client_phone, created_at, updated_at
        FROM orders
        WHERE master_id = $1
        AND appointment_datetime >= $2 
        AND appointment_datetime <= $3
        AND status NOT IN ('cancelled', 'no_show')
        ORDER BY appointment_datetime
        """
        try:
            rows = await self.db.fetch(query, master_id, start_of_day, end_of_day)
            return [self._row_to_order(row) for row in rows]
        except Exception as e:
            logger.error(f"Ошибка при получении расписания мастера {master_id} на {date.date()}: {e}")
            raise

    async def get_master_busy_times(self, master_id: int, date: datetime) -> List[tuple]:
        """Получает занятые временные слоты мастера на день"""
        query = """
        SELECT appointment_datetime, 
               appointment_datetime + INTERVAL '1 minute' * duration_minutes as end_time
        FROM orders
        WHERE master_id = $1
        AND DATE(appointment_datetime) = $2
        AND status NOT IN ('cancelled', 'no_show')
        ORDER BY appointment_datetime
        """
        try:
            rows = await self.db.fetch(query, master_id, date.date())
            return [(row['appointment_datetime'], row['end_time']) for row in rows]
        except Exception as e:
            logger.error(f"Ошибка при получении занятых слотов мастера {master_id}: {e}")
            raise

    async def get_statistics(self, start_date: datetime = None, end_date: datetime = None) -> dict:
        """Получает статистику по заказам"""
        where_clause = ""
        params = []

        if start_date and end_date:
            where_clause = "WHERE created_at >= $1 AND created_at <= $2"
            params = [start_date, end_date]
        elif start_date:
            where_clause = "WHERE created_at >= $1"
            params = [start_date]
        elif end_date:
            where_clause = "WHERE created_at <= $1"
            params = [end_date]

        query = f"""
        SELECT 
            COUNT(*) as total_orders,
            COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_orders,
            COUNT(CASE WHEN status = 'cancelled' THEN 1 END) as cancelled_orders,
            COUNT(CASE WHEN status = 'no_show' THEN 1 END) as no_show_orders,
            SUM(CASE WHEN status = 'completed' THEN total_price ELSE 0 END) as total_revenue,
            AVG(CASE WHEN status = 'completed' THEN total_price ELSE NULL END) as avg_order_value
        FROM orders
        {where_clause}
        """

        try:
            row = await self.db.fetchrow(query, *params)
            return {
                'total_orders': row['total_orders'],
                'completed_orders': row['completed_orders'],
                'cancelled_orders': row['cancelled_orders'],
                'no_show_orders': row['no_show_orders'],
                'total_revenue': float(row['total_revenue']) if row['total_revenue'] else 0.0,
                'avg_order_value': float(row['avg_order_value']) if row['avg_order_value'] else 0.0,
                'completion_rate': (row['completed_orders'] / row['total_orders'] * 100) if row[
                                                                                                'total_orders'] > 0 else 0.0
            }
        except Exception as e:
            logger.error(f"Ошибка при получении статистики заказов: {e}")
            raise

    def _row_to_order(self, row) -> Order:
        """Преобразует строку БД в объект Order"""
        return Order(
            id=row['id'],
            user_id=row['user_id'],
            master_id=row['master_id'],
            service_id=row['service_id'],
            appointment_datetime=row['appointment_datetime'],
            duration_minutes=row['duration_minutes'],
            total_price=Decimal(str(row['total_price'])),
            status=OrderStatus(row['status']),
            notes=row['notes'],
            client_name=row['client_name'],
            client_phone=row['client_phone'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
