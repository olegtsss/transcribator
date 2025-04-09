import logging
from logging import config as logging_config
from pathlib import Path

from core.config import settings

LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': LOG_FORMAT
        },
    },
    'handlers': {
        'default': {
            'formatter': 'verbose',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stderr',
        },
        'to_file': {
            'formatter': 'verbose',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': f'{settings.log_dir}/producer.log',
            'interval': settings.log_internal,
            'backupCount': settings.log_count,
            'when': settings.log_when,
            'encoding': settings.log_encoding,
        },
    },
    'loggers': {
        settings.app_title: {
            'handlers': ['default', 'to_file'],
            'level': settings.log_level
        },
    }
}
(Path(__file__).parent.parent.parent / settings.log_dir).mkdir(exist_ok=True)
logging_config.dictConfig(LOGGING)
logger = logging.getLogger(settings.app_title)


def create_uvicorn_log(
    uvicorn_access: str = 'uvicorn.access', file_name: str = 'uvicorn.log'
) -> None:
    handler_for_uvicorn = logging.handlers.TimedRotatingFileHandler(
        filename=f'{settings.log_dir}/{file_name}',
        interval=settings.log_internal, backupCount=settings.log_count,
        when=settings.log_when, encoding=settings.log_encoding
    )
    handler_for_uvicorn.setFormatter(logging.Formatter(LOG_FORMAT))
    logging.getLogger(uvicorn_access).addHandler(handler_for_uvicorn)
