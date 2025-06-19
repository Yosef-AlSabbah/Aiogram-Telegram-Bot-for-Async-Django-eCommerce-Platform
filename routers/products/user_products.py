from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from api_client.product_client import ProductClient
from aiogram.utils.i18n import I18n
from aiogram.utils.i18n import gettext as _
from keyboards.inline_keyboards.products import get_product_management_keyboard
from renderers.product_renderer import render_product_short
from utils.messaging import send_message_with_optional_photo

router = Router(name=__name__)


@router.message(Command('my_products', _('my_products'), prefix='/', ignore_case=True))
async def my_products(message: Message, i18n: I18n) -> None:
    """
    This function retrieves the user's products and displays them as separate messages,
    each with a management keyboard for product-specific actions.

    Parameters:
        message (Message): The incoming message object from Telegram
        i18n (I18n): Internationalization instance for translation support

    Returns:
        None: Messages are sent directly to the user via the message.answer method
    """

    # Retrieve all products belonging to the current user
    products = await ProductClient.my_products()

    # If no products found, inform the user and exit
    if not products:
        await message.answer(_('You have no products.'))
        return

    # Display each product as a separate message with management options
    for product in products:
        text, thumbnail_url = render_product_short(product)  # Format product details as text
        keyboard = get_product_management_keyboard(product.id)  # Create inline keyboard for this product
        await send_message_with_optional_photo(message, text, thumbnail_url, keyboard)
