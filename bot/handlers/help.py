import logging

from config import settings
from constants import Messages
from telegram import Update
from telegram.ext import ContextTypes
from utils import cancel

logger = logging.getLogger(settings.app_title)


async def get_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(
        Messages.BOT_START_MESSAGE_LOG.value, update.effective_chat.id,
        update.effective_chat.username if update.effective_chat.username else ''
    )
    await update.message.reply_text(
        text=Messages.BOT_START_MESSAGE.value, parse_mode=settings.parse_mode,
        disable_web_page_preview=True
    )
    await cancel(update=update, context=context)
