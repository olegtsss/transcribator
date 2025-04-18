import datetime as dt
import http
import json
import uuid

import aiohttp
import pytest

from tests.functional.settings import test_settings
from tests.functional.utils import generate_digits, generate_name


@pytest.mark.asyncio
async def test_create_task(get_queue):
    """Создание задание в сервисе Producer"""

    telegram_id = generate_digits()
    audio_path = generate_name()
    translate = True

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f'http://{test_settings.producer_host}:{test_settings.producer_port}/api/v1/rabbit/create_task',
            json={'telegram_id': telegram_id, 'audio_path': audio_path, 'translate': translate}
        ) as response:
            assert response.status == http.HTTPStatus.CREATED
            result = await response.json()
            assert isinstance(result, str)
            try:
                assert isinstance(uuid.UUID(result), uuid.UUID)
            except ValueError:
                assert False

    async with get_queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                broker_result = json.load(message.body)
                assert broker_result['entity_id'] == result
                assert isinstance(
                    dt.datetime.fromisoformat(broker_result['created_at']), dt.datetime
                )
                assert broker_result['telegram_id'] == telegram_id
                assert broker_result['audio_path'] == audio_path
                assert broker_result['translate'] == translate
                raise StopIteration

    telegram_id = generate_digits()
    audio_path = generate_name()
    translate = False

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f'http://{test_settings.producer_host}:{test_settings.producer_port}/api/v1/rabbit/create_task',
            json={'telegram_id': telegram_id, 'audio_path': audio_path, 'translate': translate}
        ) as response:
            assert response.status == http.HTTPStatus.CREATED
            result = await response.json()

    async with get_queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                broker_result = json.load(message.body)
                assert broker_result['entity_id'] == result
                assert isinstance(
                    dt.datetime.fromisoformat(broker_result['created_at']), dt.datetime
                )
                assert broker_result['telegram_id'] == telegram_id
                assert broker_result['audio_path'] == audio_path
                assert broker_result['translate'] == translate
                raise StopIteration
