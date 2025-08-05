from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

from src.models.users.User import User

@dataclass
class Master(User):
    id: Optional[int] = None
    telegram_id: Optional[int] = None
    username: str = ""
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    specialization: Optional[str] = None
    experience_years: int = 0
    rating: float = 0.0
    is_active: bool = True
    working_hours_start: Optional[str] = None  # "09:00"
    working_hours_end: Optional[str] = None    # "18:00"
    working_days: Optional[str] = None         # "1,2,3,4,5" (дни недели)
    service_ids: List[int] = None              # Список ID услуг, которые оказывает мастер
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        if self.service_ids is None:
            self.service_ids = []