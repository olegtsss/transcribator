import asyncio
import functools
import logging
from datetime import datetime, timedelta
from functools import lru_cache
from http import HTTPStatus
from typing import Callable

import aiohttp
import backoff
from aiohttp.client_exceptions import ClientConnectorError
from aiohttp.web import HTTPException
from openai import OpenAI
from src.config import settings
from src.constants import APP_NAME, Messanges

logger = logging.getLogger(APP_NAME)


class HttpResponseError(Exception):
    pass


class TooManyRetries(Exception):
    pass


class CircuitOpenException(Exception):
    pass


class CircuitBreaker:

    def __init__(
        self, callback, timeout: int = 10, time_window: float = 5.0, max_failures: int = 5,
        reset_interval: int = 60
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
            logger.info(Messanges.CIRCUIT_BREAKER_CLOSE.value)
            return await self._do_request(*args, **kwargs)

    def _reset(self):
        logger.info(Messanges.CIRCUIT_BREAKER_RESET.value)
        self.last_failure_time = None
        self.current_failures = 0

    async def _do_request(self, *args, **kwargs):
        try:
            self.last_request_time = datetime.now()
            return await asyncio.wait_for(self.callback(*args, **kwargs), timeout=self.timeout)
        except TimeoutError:
            logger.info(Messanges.CIRCUIT_BREAKER_CATCH_TIMEOUT.value)
        except TooManyRetries:
            logger.error(Messanges.RETRY_ERROR_FULL.value)
        self.current_failures += 1
        if self.last_failure_time is None:
            self.last_failure_time = datetime.now()


@backoff.on_exception(
    backoff.expo, ConnectionError, max_time=settings.backoff_max_time,
    max_tries=settings.backoff_max_tries
)
def get_openai_client() -> OpenAI:
    return OpenAI(
        api_key='cant-be-empty',
        base_url=f'http://{settings.proxy_host}:{settings.whisper_port}/v1/'
    )


async def retry_requests(
    coro: Callable, max_retries: int = 5, retry_interval: int = 1
) -> None:
    for retry_num in range(max_retries):
        try:
            # timeout обрабатывается в CircuitBreaker
            # return await asyncio.wait_for(coro(), timeout=timeout)
            return await coro()
        except (HTTPException, ClientConnectorError, HttpResponseError) as error:
            logger.error(Messanges.RETRY_ERROR.value, retry_num, error)
        await asyncio.sleep(retry_interval)
    raise TooManyRetries


async def http_post(
    session, telegram_id: int, message: str,
    chat_id_post: str = 'chat_id', text_post: str = 'text'
) -> str:
    logger.info('Попытка http post %s',  message[:50])
    async with session.post(
        settings.bot_url, headers=settings.http_headers,
        json={chat_id_post: telegram_id, text_post: message}
    ) as response:
        if response.status not in (HTTPStatus.OK,):
            logger.error(Messanges.ERROR_FROM_EXTERNAL_API.value, response.status)
            raise HttpResponseError
        return await response.text()


def error_handling(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as err:
            logging.exception(err)
    return wrapper


@lru_cache
def get_telegram_service() -> CircuitBreaker:
    return CircuitBreaker(retry_requests)


telegram_service = get_telegram_service()


async def raw_sent_message_to_telegram(telegram_id: int, messages: list) -> None:
    async with aiohttp.ClientSession() as session:
        for message in messages:
            if len(messages) > 1:
                await asyncio.sleep(settings.telegram_delay_for_message)
            try:
                await telegram_service.request(
                    functools.partial(http_post, session, telegram_id, message)
                )
            except CircuitOpenException:
                logger.error(
                    Messanges.MESSAGE_DONT_SEND.value, telegram_id,
                    message[:settings.logging_message_slice]
                )
