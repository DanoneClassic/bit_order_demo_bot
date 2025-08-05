from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from decimal import Decimal
from enum import Enum

class OrderStatus(Enum):
    PENDING = "pending"           # Ожидает подтверждения
    CONFIRMED = "confirmed"       # Подтверждён
    IN_PROGRESS = "in_progress"   # В процессе выполнения
    COMPLETED = "completed"       # Завершён
    CANCELLED = "cancelled"       # Отменён
    NO_SHOW = "no_show"          # Клиент не пришёл

@dataclass
class Order:
    id: Optional[int] = None
    user_id: int = 0
    master_id: int = 0
    service_id: int = 0
    appointment_datetime: Optional[datetime] = None
    duration_minutes: int = 0
    total_price: Decimal = Decimal('0.00')
    status: OrderStatus = OrderStatus.PENDING
    notes: Optional[str] = None
    client_name: Optional[str] = None
    client_phone: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
