from functools import lru_cache

import aio_pika
import backoff
from core.config import settings


class Bus:
    def __init__(self) -> None:
        self.connection = None
        self.channel = None

    @backoff.on_exception(
        backoff.expo, ConnectionError, max_time=settings.backoff_max_time,
        max_tries=settings.backoff_max_tries
    )
    async def create_connection(self) -> None:
        self.connection = await aio_pika.connect_robust(settings.rabbit_dsn)

    async def prepair_channel(self) -> None:
        self.channel = await self.connection.channel()
        await self.channel.declare_exchange(
            settings.transcribe_exchange, aio_pika.ExchangeType.DIRECT, auto_delete=True,
            durable=False
        )

    async def close_connection(self) -> None:
        await self.connection.close()


@lru_cache
def get_bus_service() -> Bus:
    return Bus()


bus_service = get_bus_service()
