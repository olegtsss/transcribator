import http

import aiohttp
import pytest

from tests.functional.settings import test_settings


@pytest.mark.asyncio
async def test_ping():
    """Проверка работоспособности api"""

    async with aiohttp.ClientSession() as session:
        async with session.get(
            f'http://{test_settings.producer_host}:'
            f'{test_settings.producer_port}/api/healthcheck/200'
        ) as response:
            assert response.status == http.HTTPStatus.OK
            assert response.content_length == 0
