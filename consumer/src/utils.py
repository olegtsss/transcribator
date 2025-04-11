import asyncio
import logging
from http import HTTPStatus
from typing import Callable

import aiohttp
from aiohttp.client_exceptions import ClientConnectorError
from aiohttp.web import HTTPException
from src.constants import APP_NAME, Messanges

logger = logging.getLogger(APP_NAME)


class HttpResponseError(Exception):
    pass


class TooManyRetries(Exception):
    pass


async def retry_requests(
    coro: Callable, max_retries: int = 5, timeout: int = 5, retry_interval: int = 1
) -> str:
    for retry_num in range(max_retries):
        try:
            return await asyncio.wait_for(coro(), timeout=timeout)
        except (HTTPException, ClientConnectorError, HttpResponseError) as error:
            logger.error(Messanges.RETRY_ERROR.value, retry_num, error)
        await asyncio.sleep(retry_interval)
    raise TooManyRetries


async def raw_sent_message_to_telegram(
    self, telegram_id: int, message: str, chat_id_post: str = 'chat_id', text_post: str = 'text'
) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.post(
            self.bot_url, headers=self.http_headers,
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
