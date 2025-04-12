import logging
import os
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from src.constants import APP_NAME

load_dotenv(dotenv_path='.env')


class Settings(BaseSettings):
    proxy_host: str = os.getenv('PROXY_HOST', '127.0.0.1')
    whisper_port: int = int(os.getenv('PROXY_WHISPER_PORT', '8080'))
    openai_model: str = 'Systran/faster-whisper-small'

    rabbit_dsn: str = (
        f"amqp://{os.getenv('RABBITMQ_DEFAULT_USER', None)}:"
        f"{os.getenv('RABBITMQ_DEFAULT_PASS', None)}"
        f"@{os.getenv('RABBITMQ_DEFAULT_HOST', None)}:"
        f"{os.getenv('RABBITMQ_DEFAULT_PORT', None)}/"
    )
    transcribe_queue: str = 'task_for_tarnscribe'
    consume_timeout: int = 1

    telegram_max_symbols_in_message: int = 4096
    telegram_delay_for_message: int = 2
    token: str = os.getenv('TELEGRAM_BOT_TOKEN', None)
    bot_url: str = f'https://api.telegram.org/bot{token}/sendMessage'
    http_headers: dict = {'User-Agent': os.getenv('USER_AGENT', None)}

    backoff_max_time: int = 30
    backoff_max_tries: int = 5

    logging_message_slice: int = 200


settings = Settings()


def configure_logging() -> None:
    app_name = APP_NAME
    log_dir = Path(__file__).parent.parent.parent / os.getenv('LOG_DIR', 'logs')
    log_dir.mkdir(exist_ok=True)
    rotating_handler = TimedRotatingFileHandler(
        log_dir / f'{app_name.lower()}.log',
        backupCount=int(os.getenv('LOG_BACKUP_COUNT', '14')),
        when=os.getenv('LOG_WHEN', 'midnight'),
        interval=int(os.getenv('LOG_INTERVAL', '1')),
        encoding=os.getenv('LOG_ENCODING', 'UTF-8'),
    )
    logging.basicConfig(
        datefmt='%d.%m.%Y %H:%M:%S',
        format='%(asctime)s - [%(levelname)s] - %(message)s',
        level=os.getenv('LOG_LEVEL', 'INFO'),
        handlers=(rotating_handler, logging.StreamHandler()),
    )
    logging.getLogger(app_name).setLevel(logging.INFO)
