from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _

def get_product_management_keyboard(product_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=_('Update'), callback_data=f'update_product_{product_id}'),
            InlineKeyboardButton(text=_('Delete'), callback_data=f'delete_product_{product_id}')
        ]
    ])

def get_public_product_keyboard(product_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=_('Show More ℹ️'), callback_data=f'show_more_{product_id}'),
            InlineKeyboardButton(text=_('Add to Favorites ❤️'), callback_data=f'add_to_favorites_{product_id}')
        ],
        [
            InlineKeyboardButton(text=_('Call Owner 📞'), callback_data=f'call_owner_{product_id}')
        ]
    ])
