import logging

from core.config import settings
from core.constants import Messanges, RoutersDescriptions
from fastapi import APIRouter, Response, status

router = APIRouter()
logger = logging.getLogger(settings.app_title)


@router.get('/200', description=RoutersDescriptions.HEALTH_200.value)
async def health() -> Response:
    logger.debug(Messanges.SEARCH_HEALTH.value)
    return Response(status_code=status.HTTP_200_OK)
