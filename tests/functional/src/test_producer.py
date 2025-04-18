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

    telegram_id_1 = generate_digits()
    audio_path_1 = generate_name()
    translate_1 = True

    telegram_id_2 = generate_digits()
    audio_path_2 = generate_name()
    translate_2 = False

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f'http://{test_settings.producer_host}:{test_settings.producer_port}/api/v1/rabbit/create_task',
            json={
                'telegram_id': telegram_id_1, 'audio_path': audio_path_1,
                'translate': translate_1
            }
        ) as response:
            assert response.status == http.HTTPStatus.CREATED
            result_1 = await response.json()
            assert isinstance(result_1, str)
            try:
                assert isinstance(uuid.UUID(result_1), uuid.UUID)
            except ValueError:
                assert False

        async with session.post(
            f'http://{test_settings.producer_host}:{test_settings.producer_port}/api/v1/rabbit/create_task',
            json={
                'telegram_id': telegram_id_2, 'audio_path': audio_path_2,
                'translate': translate_2
            }
        ) as response:
            assert response.status == http.HTTPStatus.CREATED
            result_2 = await response.json()

    async with get_queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                broker_result = json.loads(message.body.decode())
                assert broker_result['entity_id'] == result_1
                assert isinstance(
                    dt.datetime.fromisoformat(broker_result['created_at']), dt.datetime
                )
                assert broker_result['telegram_id'] == telegram_id_1
                assert broker_result['audio_path'] == audio_path_1
                assert broker_result['translate'] == translate_1
                break

        async for message in queue_iter:
            async with message.process():
                broker_result = json.loads(message.body.decode())
                assert broker_result['entity_id'] == result_2
                assert isinstance(
                    dt.datetime.fromisoformat(broker_result['created_at']), dt.datetime
                )
                assert broker_result['telegram_id'] == telegram_id_2
                assert broker_result['audio_path'] == audio_path_2
                assert broker_result['translate'] == translate_2
                break
