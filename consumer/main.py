import asyncio
import logging
import os
from asyncio import sleep
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

import aio_pika
from enum import Enum
import httpx
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(dotenv_path='.env')


APP_NAME: str = 'Consumer'


class Messanges(str, Enum):
    BACKEND_START = 'Приложение запущено'
    ERROR_FROM_EXTERNAL_API = 'При обращении к API возникла ошибка: %s'


class Worker:
    def __init__(self) -> None:
        self.proxy_host: str = os.getenv('PROXY_HOST', '127.0.0.1')
        self.proxy_port: int = int(os.getenv('PROXY_PORT', '8080'))
        self.openai_client: OpenAI = OpenAI(
            api_key='cant-be-empty', base_url=f'http://{self.proxy_host}:{self.proxy_port}/v1/'
        )
        self.openai_model: str = 'Systran/faster-whisper-small'

        self.rabbit_dsn: str = (
            f"amqp://{os.getenv('RABBITMQ_DEFAULT_USER', None)}:"
            f"{os.getenv('RABBITMQ_DEFAULT_PASS', None)}"
            f"@{os.getenv('RABBITMQ_DEFAULT_HOST', None)}:"
            f"{os.getenv('RABBITMQ_DEFAULT_PORT', None)}/"
        )
        self.transcribe_queue: str = 'task_for_tarnscribe'

        self.telegram_max_symbols_in_message: int = 4096
        self.telegram_delay_for_message: int = 2
        self.token: str = os.getenv('TELEGRAM_BOT_TOKEN', None)
        self.bot_url: str = f'https://api.telegram.org/bot{self.token}/sendMessage'
        self.http_headers: dict = {'User-Agent': os.getenv('USER_AGENT', None)}

    @staticmethod
    def error_handling(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as err:
                logging.exception(err)
        return wrapper

    async def raw_sent_messages_to_telegram(
        self, telegram_id: int, messages: list,
        chat_id_post: str = 'chat_id', text_post: str = 'text'
    ) -> None:
        async with httpx.AsyncClient() as client:
            for message in messages:
                try:
                    if len(messages) > 1:
                        await sleep(self.telegram_delay_for_message)
                    await client.post(
                        self.bot_url, headers=self.http_headers,
                        data={chat_id_post: telegram_id, text_post: message}
                    )
                except httpx.RequestError as error:
                    logging.error(Messanges.ERROR_FROM_EXTERNAL_API, error.request.url)

    @error_handling
    async def process_message(self, message: aio_pika.abc.AbstractIncomingMessage) -> None:
        async with message.process():
            # правильно принять инфу
            audio_file_path, telegram_id = message.body
            if not os.access(audio_file_path, os.R_OK):
                return
            with open(audio_file_path, mode='rb') as file:
                transcript = self.openai_client.audio.transcriptions.create(
                    model=self.openai_model, file=file
                )
            await self.raw_sent_messages_to_telegram(
                telegram_id=telegram_id,
                messages=[
                    transcript.text[i:i+self.telegram_max_symbols_in_message]
                    for i in range(0, len(transcript.text), self.telegram_max_symbols_in_message)
                ]
            )

    async def consume(self) -> None:
        try:
            connection = await aio_pika.connect_robust(self.rabbit_dsn)
            channel = await connection.channel()
            instant_queue = await channel.declare_queue(self.transcribe_queue, durable=True)
            while True:
                await instant_queue.consume(self.process_message)
        finally:
            await connection.close()


def configure_logging() -> None:
    app_name = APP_NAME
    log_dir = Path(__file__).parent.parent / os.getenv('LOG_DIR', 'logs')
    log_dir.mkdir(exist_ok=True)
    rotating_handler = TimedRotatingFileHandler(
        log_dir / f'{app_name}.log',
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


async def main() -> None:
    configure_logging()
    logging.info(Messanges.BACKEND_START)
    worker = Worker()
    await worker.consume()


if __name__ == '__main__':
    asyncio.run(main())
