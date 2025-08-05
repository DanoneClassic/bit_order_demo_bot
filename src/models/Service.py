from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from decimal import Decimal

@dataclass
class Service:
    id: Optional[int] = None
    name: str = ""
    description: Optional[str] = None
    category: str = ""
    subcategory: Optional[str] = None
    price: Decimal = Decimal('0.00')
    duration_minutes: int = 0
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None