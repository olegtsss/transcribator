import aio_pika
import pytest_asyncio

from tests.functional.settings import test_settings


@pytest_asyncio.fixture(name='get_queue')
async def get_queue():
    connection = await aio_pika.connect_robust(test_settings.rabbit_dsn)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=1)
    instant_queue = await channel.declare_queue(
        test_settings.transcribe_queue, durable=False, auto_delete=True
    )
    yield instant_queue
    await connection.close()
