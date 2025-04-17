import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv(dotenv_path='.env')


class TestSettings(BaseSettings):
    producer_host: str = '192.168.16.65'
    producer_port: int = int(os.getenv('PROXY_PRODUCER_PORT', '8001'))


test_settings = TestSettings()
