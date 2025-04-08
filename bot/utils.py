import functools
import logging
from asyncio import sleep
from typing import Any, Callable

from config import openai_client, settings
from constants import Messages
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

logger = logging.getLogger(settings.app_title)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Any:
    context.user_data.clear()
    return ConversationHandler.END


class FastApiResponseError(Exception):
    pass


def markdown_worker(text: str) -> str:
    if text:
        return (
            text.
            replace('.', r'\.').
            replace('_', r'\_').
            replace('-', r' ').
            replace('*', r'\*').
            replace('[', r'\[').
            replace(']', r'\]').
            replace('(', r'\(').
            replace(')', r'\)').
            replace('~', r'\~').
            replace('`', r'\`').
            replace('<', r'\<').
            replace('>', r'\>').
            replace('#', r'\#').
            replace('+', r'\+').
            replace('-', r'\-').
            replace('=', r'\=').
            replace('|', r'\|').
            replace('{', r'\{').
            replace('}', r'\}').
            replace('!', r'\!')
        )
    return ''


async def sent_message_to_telegram(messages: list, update: Update) -> None:
    for message in messages:
        if len(messages) > 1:
            await sleep(settings.telegram_delay_for_message)
        await update.message.reply_text(
            text=message, parse_mode=settings.parse_mode, disable_web_page_preview=True
        )


def backend_worker(audio_file_name: str) -> str:
    with open(audio_file_name, mode='rb') as file:
        transcript = openai_client.audio.transcriptions.create(
            model=settings.openai_model, file=file
        )
    return transcript.text


def chech_user_permition():
    def wrapper(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapped(*args, **kwargs) -> Any:
            update, context = args
            if update.effective_chat.id not in settings.users:
                logger.info(Messages.BOT_NOT_PERMIT.value, update.effective_chat.id)
                return await cancel(update=update, context=context)
            return await func(*args, **kwargs)
        return wrapped
    return wrapper
