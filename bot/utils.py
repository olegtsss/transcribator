import asyncio
import functools
import logging
from datetime import datetime, timedelta
from functools import lru_cache
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


class CircuitOpenException(Exception):
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


async def request_to_produse_service(data: dict) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.post(
            (
                f'http://{settings.producer_host}:{settings.producer_port}/'
                f'{Routes.PRODUCE_TASK.value}',
            ),
            json=data
        ) as response:
            if response.status not in (HTTPStatus.CREATED,):
                logger.error(Messages.TASK_REQUEST_ERROR.value, response.status)
                raise FastApiResponseError
            return await response.text()


async def retry_requests(
    coro: Callable, max_retries: int = 5, retry_interval: int = 1
) -> str:
    for retry_num in range(max_retries):
        try:
            # timeout обрабатывается в CircuitBreaker
            # return await asyncio.wait_for(coro(), timeout=timeout)
            return await coro()
        except (HTTPException, ClientConnectorError, FastApiResponseError) as error:
            logger.error(Messages.RETRY_ERROR.value, retry_num, error)
        await asyncio.sleep(retry_interval)
    raise TooManyRetries


class CircuitBreaker:

    def __init__(
        self, callback, timeout: int = 10, time_window: float = 5.0, max_failures: int = 25,
        reset_interval: int = 30
    ) -> None:
        self.callback = callback
        self.timeout = timeout
        self.time_window = time_window
        self.max_failures = max_failures
        self.reset_interval = reset_interval
        self.last_request_time = None
        self.last_failure_time = None
        self.current_failures = 0

    async def request(self, *args, **kwargs):
        if self.current_failures >= self.max_failures:
            if (
                datetime.now() >
                self.last_failure_time + timedelta(seconds=self.reset_interval)
            ):
                self._reset()
                return await self._do_request(*args, **kwargs)
            else:
                raise CircuitOpenException
        else:
            if (
                self.last_failure_time and
                datetime.now() >
                self.last_failure_time + timedelta(seconds=self.time_window)
            ):
                self._reset()
            logger.info(Messages.CIRCUIT_BREAKER_CLOSE.value)
            return await self._do_request(*args, **kwargs)

    def _reset(self):
        logger.info(Messages.CIRCUIT_BREAKER_RESET.value)
        self.last_failure_time = None
        self.current_failures = 0

    async def _do_request(self, *args, **kwargs):
        try:
            self.last_request_time = datetime.now()
            return await asyncio.wait_for(self.callback(*args, **kwargs), timeout=self.timeout)
        except TimeoutError:
            logger.info(Messages.CIRCUIT_BREAKER_CATCH_TIMEOUT.value)
        except TooManyRetries:
            logger.error(Messages.RETRY_ERROR_FULL.value)
        self.current_failures += 1
        if self.last_failure_time is None:
            self.last_failure_time = datetime.now()


@lru_cache
def get_producer_service() -> CircuitBreaker:
    return CircuitBreaker(retry_requests)


producer_service = get_producer_service()
