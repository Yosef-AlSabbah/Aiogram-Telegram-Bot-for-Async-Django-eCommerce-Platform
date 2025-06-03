from pathlib import Path

from aiogram import Dispatcher, Bot
from aiogram.utils.i18n import I18n, SimpleI18nMiddleware

from config import settings
from middlewares.auth_middleware import AuthMiddleware
from middlewares.signature_middleware import uninstall_signature_middleware, \
    install_signature_middleware
from routers import router


async def startup():
    """
    Initialize resources needed for the bot before starting.

    Sets up the signature middleware for authenticating API requests
    using the secret key from settings.
    """
    install_signature_middleware(
        secret_key=settings.SIGNATURE_AUTH_SECRET_KEY,
        backend_urls=settings.BASE_URL,  # Only your backend!
        debug=settings.DEBUG
    )
    print("🚀 Bot started with signature middleware")


async def shutdown():
    """
    Properly clean up resources when the bot is shutting down.

    Uninstalls the signature middleware to prevent any lingering effects.
    """
    uninstall_signature_middleware()
    print("🛑 Bot stopped")


async def turn_i18n(dp: Dispatcher):
    """
    Initialize internationalization (i18n) settings for the bot.

    Sets up the I18n instance and middleware to handle translations.
    """
    # Create an I18n instance
    i18n = I18n(
        path=Path(__file__).parent / "locales",
        default_locale="en",
        domain="messages"
    )

    # Set up the middleware
    middleware = SimpleI18nMiddleware(i18n=i18n)
    dp.message.middleware(middleware)
    dp.callback_query.middleware(middleware)

    print("🌐 Internationalization middleware installed")


async def main():
    """
    Main application entry point that orchestrates the bot lifecycle.

    Initializes the bot with its token, sets up the dispatcher with all routes,
    and handles the polling loop with proper startup and shutdown procedures.
    """
    await startup()

    # Initialize the bot with the token from settings
    bot = Bot(token=settings.BOT_TOKEN)

    # Create a Dispatcher and set up routing
    dp = Dispatcher()

    # Set up middlewares
    await turn_i18n(dp)
    dp.message.middleware(AuthMiddleware())

    dp.include_router(router)

    try:
        # Start the bot and listen for incoming messages
        await dp.start_polling(bot)
    finally:
        # Ensure proper cleanup happens even if there's an error
        await shutdown()


if __name__ == "__main__":
    from asyncio import run as run_async
    from logging import basicConfig, DEBUG

    # Configure logging for better debugging
    basicConfig(
        level=DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Run the main async function
    run_async(main())
