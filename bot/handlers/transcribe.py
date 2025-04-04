import logging
import os
from typing import Optional

from config import settings
from constants import Buttons, Commands, Messages
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (CommandHandler, ContextTypes, ConversationHandler,
                          filters, MessageHandler)
from utils import (backend_worker, cancel, chech_user_permition,
                   sent_message_to_telegram)

logger = logging.getLogger(settings.app_title)


START: int = 1


@chech_user_permition()
async def print_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        Messages.START_TRANSCRIBE.value,
        reply_markup=ReplyKeyboardMarkup(
            [[Buttons.STOP.value]],
            one_time_keyboard=True, resize_keyboard=True,
            input_field_placeholder=Buttons.PLACE_HOLDER.value
        ),
        parse_mode=settings.parse_mode
    )
    return START


@chech_user_permition()
async def audio_worker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[int]:
    audio_file = update.message.audio
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
        return START
    # Audio(duration=12, file_id='CQACAgIAAxkBAAMKZ-57hMAecHH3mjSwRsHTsth6fGUAAgR8AAJVWXBLOPrBRdcx1uc2BA',
    # file_name='AUDIO-2025-04-03-09-08-24.m4a', file_size=156336, file_unique_id='AgADBHwAAlVZcEs', mime_type='audio/mpeg')
    new_file = await context.bot.get_file(audio_file.file_id)
    audio_path = f'{settings.temp_dir}/{audio_file.file_unique_id}.m4a'
    audio_path = await new_file.download_to_drive(audio_path)
    text = backend_worker(audio_path)
    if os.access(audio_path, os.R_OK):
        os.remove(audio_path)
    await sent_message_to_telegram(
        messages=[text if text else Messages.EMPTY_TRANSCRIBE.value], update=update
    )
    await update.message.reply_text(
        Messages.REPEAT_TRANSCRIBE.value,
        reply_markup=ReplyKeyboardMarkup(
            [[Buttons.STOP.value]],
            one_time_keyboard=True, resize_keyboard=True,
            input_field_placeholder=Buttons.PLACE_HOLDER.value
        ),
        parse_mode=settings.parse_mode
    )
    return START


main_handler = ConversationHandler(
    entry_points=[CommandHandler(Commands.TRANSCRIBE.value, print_buttons)],
    states={
        START: [
            MessageHandler(
                filters.AUDIO & ~(filters.COMMAND | filters.Regex(Buttons.STOP.value)),
                audio_worker
            )
        ],
    },
    fallbacks=[
        MessageHandler(filters.Regex(Buttons.STOP.value), print_buttons),
        MessageHandler(filters.ALL, cancel)
    ]
)
