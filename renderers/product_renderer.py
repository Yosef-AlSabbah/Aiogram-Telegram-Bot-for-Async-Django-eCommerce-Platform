from typing import Tuple, Optional
from aiogram.utils.markdown import hbold, hitalic
from api.structure.models import Product


def render_product_short(product: Product) -> Tuple[str, Optional[str]]:
    """
    Renders a short description of a product and returns the text and thumbnail URL.
    It's recommended to use a default image if product.thumbnail is None.
    """
    text = (
        f"{hbold(product.name)}\n\n"
        f"{hbold('Price:')} {product.price}\n"
        f"{hbold('Category:')} {product.category_name}\n"
    )
    return text, product.thumbnail


def render_product_details(product: Product) -> Tuple[str, Optional[str]]:
    """
    Renders a detailed description of a product and returns the text and thumbnail URL.
    It's recommended to use a default image if product.thumbnail is None.
    """
    text = (
        f"{hbold(product.name)}\n\n"
        f"{hbold('Price:')} {product.price}\n"
        f"{hbold('Category:')} {product.category_name}\n"
        f"{hbold('Status:')} {product.approval_status}\n"
        f"{hbold('Owner:')} {product.user_username}\n"
        f"{hbold('Tags:')} {', '.join(product.tags)}\n\n"
        f"{hbold('Description:')}\n{product.short_description}\n\n"
        f"{hitalic(f'Created at: {product.created_at.strftime('%Y-%m-%d %H:%M')}')}\n"
        f"{hitalic(f'Last updated: {product.updated_at.strftime('%Y-%m-%d %H:%M')}')}"
    )
    return text, product.thumbnail
