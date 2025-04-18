import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv(dotenv_path='.env')


class Settings(BaseSettings):
    app_title: str = os.getenv('APP_TITLE', 'Producer')

    log_level: str = os.getenv('LOG_LEVEL', 'INFO')
    log_dir: str = os.getenv('LOG_DIR', 'logs')
    log_count: int = int(os.getenv('LOG_BACKUP_COUNT', '14'))
    log_when: str = os.getenv('LOG_WHEN', 'midnight')
    log_internal: int = int(os.getenv('LOG_INTERVAL', '1'))
    log_encoding: str = os.getenv('LOG_ENCODING', 'UTF-8')

    host: str = os.getenv('PRODUCER_LISTENING_IP', '127.0.0.1')
    port: int = int(os.getenv('PRODUCER_LISTENING_PORT', '8001'))

    rabbit_dsn: str = (
        f"amqp://{os.getenv('RABBITMQ_DEFAULT_USER', 'guest')}:"
        f"{os.getenv('RABBITMQ_DEFAULT_PASS', 'guest')}"
        f"@{os.getenv('RABBITMQ_DEFAULT_HOST', '127.0.0.1')}:"
        f"{os.getenv('RABBITMQ_DEFAULT_PORT', '5672')}/"
    )
    transcribe_exchange: str = 'produce_exchange'
    transcribe_queue: str = 'tasks'

    timeout_for_requests: int = 10
    backoff_max_time: int = 30
    backoff_max_tries: int = 5


settings = Settings()
