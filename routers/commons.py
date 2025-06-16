import aiogram.utils.markdown as md
from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.utils.i18n import I18n
from aiogram.utils.i18n import gettext as _

router = Router(name=__name__)


@router.message(CommandStart())
async def command_start(message: Message, i18n: I18n) -> None:
    await message.reply(
        _("Welcome! This is a bot that can help you with various tasks. Type /help to see what I can do for you."),
    )


@router.message(Command('help', prefix='/'))
async def command_help(message: Message, i18n: I18n) -> None:
    await message.reply(
        md.text(
            md.hbold(_('Help')),
            md.text(_('Available commands:')),
            md.text('/login - ' + _('Login to your account')),
            md.text('/register - ' + _('Create a new account')),
            md.text('/help - ' + _('Show this help message')),
            md.text('/clear_chat - ' + _('Clear your conversation history with the assistant')),
            md.text(_('You can also chat with our AI assistant in natural language for product information and support.')),
            sep='\n'
        ),
        parse_mode=ParseMode.HTML
    )


@router.message(F.text.startswith('!'))
async def handle_unauthorized_command(message: Message, i18n: I18n):
    await message.reply(
        md.text(
            md.hbold(_("Permission Denied")),
            md.text(_("You don't have permission to use this command.")),
            md.text(_("Only authenticated"), md.hitalic(_("staff members")), _("can use these commands.")),
            sep='\n'
        ),
        parse_mode=ParseMode.HTML
    )
