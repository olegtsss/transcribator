import asyncio
import functools
import logging
from http import HTTPStatus
from typing import Any, Callable

import aiohttp
from aiohttp.client_exceptions import ClientConnectorError
from aiohttp.web import HTTPException
from config import settings
from constants import Messages, Routes
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

logger = logging.getLogger(settings.app_title)


class FastApiResponseError(Exception):
    pass


class TooManyRetries(Exception):
    pass


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Any:
    context.user_data.clear()
    return ConversationHandler.END


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
            await asyncio.sleep(settings.telegram_delay_for_message)
        await update.message.reply_text(
            text=message, parse_mode=settings.parse_mode, disable_web_page_preview=True
        )


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


async def request_to_produse_service(path: str, data: dict) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.post(
            (
                f'http://{settings.producer_host}:{settings.producer_port}/'
                f'{Routes.PRODUCE_TASK.value}'
            ),
            json=data
        ) as response:
            if response.status not in (HTTPStatus.CREATED,):
                logger.error(Messages.TASK_REQUEST_ERROR.value, response.status)
                raise FastApiResponseError
            return await response.text()


async def retry_requests(
    coro: Callable, max_retries: int = 5, timeout: int = 5, retry_interval: int = 1
) -> str:
    for retry_num in range(max_retries):
        try:
            return await asyncio.wait_for(coro(), timeout=timeout)
        except (TimeoutError, HTTPException, ClientConnectorError, FastApiResponseError) as error:
            logger.error(Messages.RETRY_ERROR.value, retry_num, error)
        await asyncio.sleep(retry_interval)
    raise TooManyRetries
