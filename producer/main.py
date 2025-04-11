import logging
from contextlib import asynccontextmanager

import uvicorn
from api.routers import main_router
from bus.rabbit import bus_service
from core.config import settings
from core.constants import Differents, Messanges
from core.middlewares import create_uvicorn_log
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger(settings.app_title)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.debug(Messanges.BACKEND_START.value)
    create_uvicorn_log()
    await bus_service.create_connection()
    await bus_service.prepair_channel()
    yield
    await bus_service.close_connection()


app = FastAPI(title=settings.app_title, lifespan=lifespan, docs_url=None, redoc_url=None)
# app = FastAPI(title=settings.app_title, lifespan=lifespan, docs_url='/docs', redoc_url='/redoc')
app.include_router(main_router)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    logger.error(exc)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=exc.errors(),
    )


@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    logger.exception(exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={Differents.DETAIL.value: Messanges.SERVER_ERROR.value},
    )


if __name__ == '__main__':
    uvicorn.run('main:app', host=settings.host, port=settings.port)
