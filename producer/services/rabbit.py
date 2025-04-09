import logging
from functools import lru_cache
from typing import List, Optional

from core.config import settings
from core.constants import Messanges
from fastapi.encoders import jsonable_encoder
from schemas.rabbit import LoadData


logger = logging.getLogger(settings.app_title)


class RabbitService:

    async def load_data_to_rabbit(self, LoadData) -> str:
        logger.info()
        return data


@lru_cache
def get_rabbit_service() -> RabbitService:
    return RabbitService()


rabbit_service = get_rabbit_service()
