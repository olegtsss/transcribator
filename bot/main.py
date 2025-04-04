from config import configure_logging, settings
from constants import Commands
from handlers.help import get_start
from handlers.transcribe import main_handler
from telegram.ext import ApplicationBuilder, CommandHandler


def create_bot():
    application = ApplicationBuilder().token(settings.telegram_bot_token).build()
    application.add_handler(CommandHandler(Commands.START.value, get_start))
    application.add_handler(handler=main_handler)
    return application


def init_polling():
    application = create_bot()
    application.run_polling()


if __name__ == '__main__':
    configure_logging()
    init_polling()
