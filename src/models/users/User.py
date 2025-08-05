from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class User:
    id: Optional[int] = None
    telegram_id: Optional[int] = None
    username: str = ""
    created_at: Optional[datetime] = None