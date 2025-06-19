# language: python
import asyncio
from datetime import datetime
from typing import List, Dict, Any

import aiohttp

from api.structure.models import Product
from ..config import settings


class ProductClient:
    BASE_URL = settings.PRODUCTSS_API_URL

    @classmethod
    async def _create_product_from_data(cls, data: Dict[str, Any]) -> Product:
     # Convert date strings to datetime objects
     data["created_at"] = datetime.fromisoformat(data["created_at"])
     data["updated_at"] = datetime.fromisoformat(data["updated_at"])
     # Create Product instance with unpacked dictionary
     return Product(**data)

    @classmethod
    async def list_products(cls) -> List[Product]:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{cls.BASE_URL}/") as response:
                data = await response.json()
                return await asyncio.gather(*[cls._create_product_from_data(item) for item in data])

    @classmethod
    async def create_product(cls, product_data: Dict[str, Any]) -> Product:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{cls.BASE_URL}/", json=product_data) as response:
                data = await response.json()
                return await cls._create_product_from_data(data)

    @classmethod
    async def get_product(cls, product_id: int) -> Product:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{cls.BASE_URL}/{product_id}/") as response:
                data = await response.json()
                return await cls._create_product_from_data(data)

    @classmethod
    async def update_product(cls, product_id: int, product_data: Dict[str, Any]) -> Product:
        async with aiohttp.ClientSession() as session:
            async with session.put(f"{cls.BASE_URL}/{product_id}/", json=product_data) as response:
                data = await response.json()
                return await cls._create_product_from_data(data)

    @classmethod
    async def partial_update_product(cls, product_id: int, product_data: Dict[str, Any]) -> Product:
        async with aiohttp.ClientSession() as session:
            async with session.patch(f"{cls.BASE_URL}/{product_id}/", json=product_data) as response:
                data = await response.json()
                return await cls._create_product_from_data(data)

    @classmethod
    async def delete_product(cls, product_id: int) -> None:
        async with aiohttp.ClientSession() as session:
            await session.delete(f"{cls.BASE_URL}/{product_id}/")

    @classmethod
    async def my_products(cls) -> List[Product]:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{cls.BASE_URL}/mine/") as response:
                data = await response.json()
                return await asyncio.gather(*[cls._create_product_from_data(item) for item in data])
