import logging
from functools import lru_cache
from typing import List, Optional

from core.config import settings
from core.constants import Messanges
from fastapi.encoders import jsonable_encoder
from schemas.base import LoadData
from bus.rabbit import bus_service
from fastapi import HTTPException, status
import aio_pika


logger = logging.getLogger(settings.app_title)


class ProducerService:

    async def load_data(self, data: LoadData) -> str:
        body = data.model_dump_json()
        await bus_service.channel.default_exchange.publish(
            aio_pika.Message(body=body.encode()), routing_key=settings.transcribe_queue
        )
        return data


@lru_cache
def get_producer_service() -> ProducerService:
    return ProducerService()


producer_service = get_producer_service()
