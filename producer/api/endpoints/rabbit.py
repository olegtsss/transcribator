import logging

from core.config import settings
from core.constants import Descriptions, Messanges
from core.utils import controlled_timeout_task
from fastapi import APIRouter, status
from schemas.task import LoadData
from services.producer import producer_service

router = APIRouter()
logger = logging.getLogger(settings.app_title)


@router.post(
    '/create_task',
    description=Descriptions.CREATE_TASK.value, status_code=status.HTTP_201_CREATED
)
@controlled_timeout_task(timeout=settings.timeout_for_requests)
async def create_task(data: LoadData) -> str:
    logger.info(Messanges.RECEIVE_DATA_FOR_PRODUCE.value, data)
    return await producer_service.load_data(data)
