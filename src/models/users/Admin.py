from dataclasses import dataclass
from typing import Optional
from datetime import datetime

from src.models.users.User import User


@dataclass
class Admin(User):
    id: Optional[int] = None
    telegram_id: Optional[int] = None
    username: str = ""
    name: Optional[str] = None
    created_at: Optional[datetime] = None
