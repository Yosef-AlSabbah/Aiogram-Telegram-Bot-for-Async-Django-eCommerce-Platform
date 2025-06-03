from dataclasses import dataclass
from typing import List
from datetime import datetime

@dataclass
class Product:
    id: int
    name: str
    slug: str
    short_description: str
    price: float
    category_name: str
    owner: str
    user_username: str
    tags: List[str]
    thumbnail: str
    approval_status: str
    created_at: datetime
    updated_at: datetime

@dataclass
class User:
    id: int
    username: str
    first_name: str
    last_name: str
    phone: str
    balance: float
    date_joined: datetime
    is_active: bool
    is_staff: bool