from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from api_client.product_client import ProductClient
from aiogram.utils.i18n import I18n
from aiogram.utils.i18n import gettext as _
from keyboards.inline_keyboards.products import get_public_product_keyboard
from renderers.product_renderer import render_product_short
from utils.messaging import send_message_with_optional_photo

router = Router(name=__name__)


@router.message(Command('products', _('products'), prefix='/', ignore_case=True))
async def list_products(message: Message, i18n: I18n) -> None:
    """
    This handler will be called when user sends `/products` command
    """
    products = await ProductClient.list_products()
    if not products:
        await message.answer(_('There are no products available at the moment.'))
        return

    for product in products:
        text, thumbnail_url = render_product_short(product)
        keyboard = get_public_product_keyboard(product.id)
        await send_message_with_optional_photo(message, text, thumbnail_url, keyboard)
