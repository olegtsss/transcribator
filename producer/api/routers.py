from api.endpoints.health import router as health_router
from api.endpoints.rabbit import router as rabbit_router
from core.constants import Descriptions
from fastapi import APIRouter

main_router = APIRouter(prefix='/api')
main_router.include_router(
    rabbit_router,
    prefix='v1/rabbit',
    tags=[Descriptions.RABBIT.value]
)
main_router.include_router(
    health_router,
    prefix='v1/healthcheck',
    tags=[Descriptions.HEALTH.value]
)
