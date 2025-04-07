import logging
import os
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from pydantic_settings import BaseSettings

load_dotenv(dotenv_path='.env')
BASE_DIR = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    app_title: str = os.getenv('APP_TITLE', 'Bot')

    log_level: str = os.getenv('LOG_LEVEL', 'INFO')
    log_dir: str = os.getenv('LOG_DIR', 'logs')
    log_count: int = int(os.getenv('LOG_BACKUP_COUNT', '14'))
    log_when: str = os.getenv('LOG_WHEN', 'midnight')
    log_internal: int = int(os.getenv('LOG_INTERVAL', '1'))
    log_encoding: str = os.getenv('LOG_ENCODING', 'UTF-8')

    proxy_host: str = os.getenv('PROXY_HOST', '127.0.0.1')
    proxy_port: int = int(os.getenv('PROXY_PORT', '8080'))

    openai_model: str = 'Systran/faster-whisper-small'

    telegram_bot_token: str = os.getenv('TELEGRAM_BOT_TOKEN', None)
    users: tuple = tuple(
        int(telegram_id) for telegram_id in os.getenv('TELEGRAM_USERS', '').split(',')
    )
    parse_mode: str = 'MarkdownV2'
    telegram_max_symbols_in_message: int = 4096
    telegram_delay_for_message: int = 2
    format_date_time: str = '%Y.%m.%d %H:%M'
    slice_for_logging_message: int = 100

    timeout_for_request: int = 60
    max_count_requests: int = 10
    max_audio_file_size: int = 1024 * 1000 * 512  # 512 Mb

    temp_dir: str = os.getenv('ROOT_TEMP_DIR', None)
    if temp_dir:
        os.makedirs('/'.join(temp_dir.split('/')), exist_ok=True)
    else:
        temp_dir: Path = Path(__file__).parent.parent / 'temp'
        temp_dir.mkdir(exist_ok=True)


settings = Settings()
openai_client = OpenAI(
    api_key='cant-be-empty', base_url=f'http://{settings.proxy_host}:{settings.proxy_port}/v1/'
)


def configure_logging() -> None:
    log_dir = Path(__file__).parent.parent / settings.log_dir
    log_dir.mkdir(exist_ok=True)
    rotating_handler = TimedRotatingFileHandler(
        log_dir / 'bot.log',
        backupCount=settings.log_count,
        when=settings.log_when,
        interval=settings.log_internal,
        encoding=settings.log_encoding,
    )
    logging.basicConfig(
        datefmt='%d.%m.%Y %H:%M:%S',
        format='%(asctime)s - [%(levelname)s] - %(message)s',
        level=settings.log_level,
        handlers=(rotating_handler, logging.StreamHandler()),
    )
    # Ручное логирование
    logging.getLogger(settings.app_title).setLevel(logging.INFO)
    # Логирование python-telegram-bot
    logging.getLogger('httpx').setLevel(logging.WARNING)
