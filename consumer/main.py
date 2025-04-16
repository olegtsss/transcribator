import asyncio
import logging
import os
from asyncio import Lock, sleep
from googletrans import Translator
import aio_pika
import backoff
from openai import OpenAI
from pydantic import ValidationError
from src.config import configure_logging, settings
from src.constants import APP_NAME, Messanges
from src.schemas import LoadData
from src.utils import (error_handling, get_openai_client, translate,
                       raw_sent_message_to_telegram)

logger = logging.getLogger(APP_NAME)


class Worker:

    def __init__(self, openai_client: OpenAI, lock: Lock, translator: Translator) -> None:
        self.openai_client = openai_client
        self.lock = lock
        self.translator = translator

    @error_handling
    async def process_message(self, message: aio_pika.abc.AbstractIncomingMessage) -> None:
        async with self.lock:
            async with message.process():
                try:
                    data = LoadData.model_validate_json(message.body.decode())
                except ValidationError:
                    logger.error(Messanges.VALIDATION_ERROR.value, message.body.decode())
                    return
            if not os.access(data.audio_path, os.R_OK):
                logger.error(Messanges.FILE_NOT_EXIST.value, data.audio_path)
                return
            with open(data.audio_path, mode='rb') as file:
                transcript = self.openai_client.audio.transcriptions.create(
                    model=settings.openai_model, file=file
                )
            if transcript.text:
                logger.info(
                    Messanges.TRANSCRIPT_SUCCESS.value, data.audio_path, len(transcript.text)
                )
                text = Messanges.ANSWER.value.format(
                    entity_id=f'{data.entity_id}'.split('-')[-1],
                    text=await translate(self.translator, transcript.text) if data.translate else transcript.text
                )
            else:
                text = Messanges.EMPTY_TRANSCRIBE.value

            messages = [
                text[i:i+settings.telegram_max_symbols_in_message]
                for i in range(0, len(text), settings.telegram_max_symbols_in_message)
            ]
            await raw_sent_message_to_telegram(data.telegram_id, messages)
        os.remove(data.audio_path)
        logger.info(Messanges.AUDIO_DELETE.value, data.audio_path)

    @backoff.on_exception(
        backoff.expo, ConnectionError, max_time=settings.backoff_max_time,
        max_tries=settings.backoff_max_tries
    )
    async def consume(self, count: int = 1) -> None:
        connection = await aio_pika.connect_robust(settings.rabbit_dsn)
        try:
            channel = await connection.channel()
            await channel.set_qos(prefetch_count=count)
            instant_queue = await channel.declare_queue(
                settings.transcribe_queue, durable=False, auto_delete=True
            )
            while True:
                await instant_queue.consume(callback=self.process_message)
                await sleep(settings.consume_timeout)
        finally:
            await connection.close()


async def main() -> None:
    configure_logging()
    logging.info(Messanges.BACKEND_START.value)
    lock = Lock()
    openai_client = get_openai_client()
    translator = Translator()
    worker = Worker(openai_client, lock, translator)
    await worker.consume()


if __name__ == '__main__':
    asyncio.run(main())
