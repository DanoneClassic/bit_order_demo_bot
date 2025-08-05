from dataclasses import dataclass
from typing import Optional
from datetime import datetime

from src.models.users.User import User


@dataclass
class Customer(User):
    id: Optional[int] = None
    telegram_id: Optional[int] = None
    username: str = ""
    created_at: Optional[datetime] = None
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
