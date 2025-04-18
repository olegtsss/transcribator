import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv(dotenv_path='.env')


class TestSettings(BaseSettings):
    producer_host: str = '192.168.16.65'
    producer_port: int = int(os.getenv('PROXY_PRODUCER_PORT', '8001'))
    rabbit_dsn: str = (
        f"amqp://{os.getenv('RABBITMQ_DEFAULT_USER', None)}:"
        f"{os.getenv('RABBITMQ_DEFAULT_PASS', None)}"
        f"@{producer_host}:{os.getenv('RABBITMQ_DEFAULT_PORT', None)}/"
    )
    transcribe_queue: str = 'tasks'


test_settings = TestSettings()
