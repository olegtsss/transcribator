import logging
from functools import lru_cache
from typing import Optional

import aio_pika
from bus.rabbit import bus_service
from core.config import settings
from core.constants import Messanges
from schemas.task import LoadData

logger = logging.getLogger(settings.app_title)


class ProducerService:

    async def load_data(self, data: LoadData) -> Optional[str]:
        try:
            await bus_service.channel.default_exchange.publish(
                aio_pika.Message(body=data.model_dump_json().encode()),
                routing_key=settings.transcribe_queue,
            )
            logger.info(Messanges.PRODUCE_SUCCESS.value, data)
            return str(data.entity_id)
        except RuntimeError:
            logger.error(Messanges.PRODUCE_ERROR, data)


@lru_cache
def get_producer_service() -> ProducerService:
    return ProducerService()


producer_service = get_producer_service()
