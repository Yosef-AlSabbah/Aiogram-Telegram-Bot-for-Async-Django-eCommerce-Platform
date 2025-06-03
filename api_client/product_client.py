# language: python
import aiohttp
from api.structure.models import Product
from datetime import datetime
from ..config import settings
class ProductClient:
    BASE_URL = settings.API_V1_URL # TODO modify this

    async def get_product(self, slug: str) -> Product:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.BASE_URL}/{slug}") as response:
                data = await response.json()
                product = Product(
                    id=data["id"],
                    name=data["name"],
                    slug=data["slug"],
                    short_description=data["short_description"],
                    price=data["price"],
                    category_name=data["category_name"],
                    owner=data["owner"],
                    user_username=data["user_username"],
                    tags=data["tags"],
                    thumbnail=data["thumbnail"],
                    approval_status=data["approval_status"],
                    created_at=datetime.fromisoformat(data["created_at"]),
                    updated_at=datetime.fromisoformat(data["updated_at"])
                )
                return product