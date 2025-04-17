import functools
import logging
import os

from config import settings
from constants import Buttons, Commands, Messages
from schemas.task import LoadData
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (CommandHandler, ContextTypes, ConversationHandler,
                          filters, MessageHandler)
from utils import (cancel, chech_user_permition, CircuitOpenException,
                   producer_service, request_to_produse_service)

logger = logging.getLogger(settings.app_title)


START, TRANSCRIBE, TRANSLATE = range(3)


@chech_user_permition()
async def print_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info(Messages.PRINT_BUTTONS.value, update.effective_chat.id)
    await update.message.reply_text(
        Messages.MODE_SELECT.value,
        reply_markup=ReplyKeyboardMarkup(
            [[Buttons.TRANSCRIBE.value], [Buttons.TRANSLATE.value]],
            one_time_keyboard=True, resize_keyboard=True,
            input_field_placeholder=Buttons.PLACE_HOLDER_MODE.value
        ),
        parse_mode=settings.parse_mode
    )
    return START


@chech_user_permition()
async def mode_worker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    mode = update.message.text
    if not mode:
        return await print_buttons(update, context)
    await update.message.reply_text(
        Messages.START_TRANSCRIBE.value,
        reply_markup=ReplyKeyboardMarkup(
            [[Buttons.STOP.value]],
            one_time_keyboard=True, resize_keyboard=True,
            input_field_placeholder=Buttons.PLACE_HOLDER.value
        ),
        parse_mode=settings.parse_mode
    )
    if mode == Buttons.TRANSCRIBE.value:
        return TRANSCRIBE
    elif mode == Buttons.TRANSLATE.value:
        return TRANSLATE
    return await print_buttons(update, context)


@chech_user_permition()
async def audio_pre_worker_translate(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    return await audio_worker(update, context)


@chech_user_permition()
async def audio_pre_worker_transcribe(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    return await audio_worker(update, context, translate=False)


@chech_user_permition()
async def audio_worker(
    update: Update, context: ContextTypes.DEFAULT_TYPE, audio_mode: str = 'audio',
    translate: bool = True
) -> int:
    logger.info(
        Messages.MODE_SELECT_DONE.value,
        update.effective_chat.id,
        Messages.TRANSLATE.value if translate else Messages.TRANSCRIBE.value
    )
    audio_file = update.message.audio or update.message.voice
    if not audio_file:
        await update.message.reply_text(
            Messages.REPEAT_TRANSCRIBE.value,
            reply_markup=ReplyKeyboardMarkup(
                [[Buttons.STOP.value]],
                one_time_keyboard=True, resize_keyboard=True,
                input_field_placeholder=Buttons.PLACE_HOLDER.value
            ),
            parse_mode=settings.parse_mode
        )
        return TRANSLATE if translate else TRANSCRIBE

    logger.info(Messages.AUDIO_RECEIVE.value, update.effective_chat.id, audio_file.duration)
    if audio_file.file_size > settings.max_audio_file_size:
        await update.message.reply_text(
            f'{Messages.FILE_VERY_BIG.value} {Messages.REPEAT_TRANSCRIBE.value}',
            reply_markup=ReplyKeyboardMarkup(
                [[Buttons.STOP.value]],
                one_time_keyboard=True, resize_keyboard=True,
                input_field_placeholder=Buttons.PLACE_HOLDER.value
            ),
            parse_mode=settings.parse_mode
        )
        return TRANSLATE if translate else TRANSCRIBE

    file_type = audio_file.mime_type.split('/')
    if file_type[0] != audio_mode:
        await update.message.reply_text(
            Messages.REPEAT_TRANSCRIBE.value,
            reply_markup=ReplyKeyboardMarkup(
                [[Buttons.STOP.value]],
                one_time_keyboard=True, resize_keyboard=True,
                input_field_placeholder=Buttons.PLACE_HOLDER.value
            ),
            parse_mode=settings.parse_mode
        )
        return TRANSLATE if translate else TRANSCRIBE

    new_file = await context.bot.get_file(audio_file.file_id)
    audio_path = f'{settings.temp_dir}/{audio_file.file_unique_id}.{file_type[1]}'
    logger.info(Messages.AUDIO_DOWNLOAD.value, audio_path)
    await new_file.download_to_drive(audio_path)

    try:
        produser_task_id: str = await producer_service.request(
            functools.partial(
                request_to_produse_service,
                LoadData(
                    telegram_id=update.effective_chat.id, audio_path=audio_path,
                    translate=translate
                ).dict()
            )
        )
        logger.info(Messages.TASK_ID.value, produser_task_id)
        if produser_task_id:
            await update.message.reply_text(
                Messages.TASK_CREATE.value.format(
                    task_id=produser_task_id.split('-')[-1].replace('"', '')
                ),
                reply_markup=ReplyKeyboardMarkup(
                    [[Buttons.STOP.value]],
                    one_time_keyboard=True, resize_keyboard=True,
                    input_field_placeholder=Buttons.PLACE_HOLDER.value
                ),
                parse_mode=settings.parse_mode
            )
            return TRANSLATE if translate else TRANSCRIBE
    except CircuitOpenException:
        logger.error(Messages.CIRCUIT_BREAKER_OPEN.value)
    if os.access(audio_path, os.R_OK):
        os.remove(audio_path)
        logger.info(Messages.AUDIO_DELETE.value, audio_path)
    await update.message.reply_text(
        Messages.TASK_ERROR.value,
        reply_markup=ReplyKeyboardMarkup(
            [[Buttons.STOP.value]],
            one_time_keyboard=True, resize_keyboard=True,
            input_field_placeholder=Buttons.PLACE_HOLDER.value
        ),
        parse_mode=settings.parse_mode
    )
    return TRANSLATE if translate else TRANSCRIBE


main_handler = ConversationHandler(
    entry_points=[CommandHandler(Commands.TRANSCRIBE.value, print_buttons)],
    states={
        START: [MessageHandler(filters.TEXT & ~(filters.COMMAND), mode_worker)],
        TRANSCRIBE: [
            MessageHandler(
                (
                    filters.AUDIO & ~(filters.COMMAND | filters.Regex(Buttons.STOP.value))
                ) | (
                    filters.FORWARDED & ~(filters.COMMAND | filters.Regex(Buttons.STOP.value))
                ) | (
                    filters.VOICE & ~(filters.COMMAND | filters.Regex(Buttons.STOP.value))
                ),
                audio_pre_worker_transcribe
            )
        ],
        TRANSLATE: [
            MessageHandler(
                (
                    filters.AUDIO & ~(filters.COMMAND | filters.Regex(Buttons.STOP.value))
                ) | (
                    filters.FORWARDED & ~(filters.COMMAND | filters.Regex(Buttons.STOP.value))
                ) | (
                    filters.VOICE & ~(filters.COMMAND | filters.Regex(Buttons.STOP.value))
                ),
                audio_pre_worker_translate
            )
        ],
    },
    fallbacks=[
        MessageHandler(filters.Regex(Buttons.STOP.value), print_buttons),
        # MessageHandler(filters.ALL, cancel)
        MessageHandler(filters.ALL, print_buttons)
    ]
)
