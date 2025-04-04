import logging
from typing import Optional

from config import settings

from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (CommandHandler, ContextTypes, ConversationHandler,
                          filters, MessageHandler)
from utils import cancel, chech_user_permition, backend_worker, sent_message_to_telegram
from constants import Commands, Buttons, Messages

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
    voice = update.message.audio
    # if not voice:
    #     await update.message.reply_text(
    #         Messages.REPEAT_TRANSCRIBE.value,
    #         reply_markup=ReplyKeyboardMarkup(
    #             [[Buttons.STOP.value]],
    #             one_time_keyboard=True, resize_keyboard=True,
    #             input_field_placeholder=Buttons.PLACE_HOLDER.value
    #         ),
    #         parse_mode=settings.parse_mode
    #     )
    #     return START
    audio_file = update.message.audio
    # Audio(duration=12, file_id='CQACAgIAAxkBAAMKZ-57hMAecHH3mjSwRsHTsth6fGUAAgR8AAJVWXBLOPrBRdcx1uc2BA',
    # file_name='AUDIO-2025-04-03-09-08-24.m4a', file_size=156336, file_unique_id='AgADBHwAAlVZcEs', mime_type='audio/mpeg')
    new_file = await context.bot.get_file(audio_file.file_id)
    audio_path = f'{settings.temp_dir}/{audio_file.file_unique_id}.m4a'
    audio_path = await new_file.download_to_drive(audio_path)
    # await new_file.download(audio_path)
    text = backend_worker(audio_path)
    await sent_message_to_telegram(messages=[text], update=update)
    # task = asyncio.create_task(
    #     backend_worker(
    #         route=BackendRoutes.TRANSCRIBATIONS.value,
    #         update=update,
    #     )
    # )
    # count = 0
    # while not task.done() and count < settings.max_count_requests:
    #     try:
    #         await asyncio.wait_for(asyncio.shield(task), settings.timeout_for_request)
    #     except TimeoutError:
    #         await update.message.reply_text(
    #             text=Messages.FIND_CONTINUE.value, parse_mode=settings.parse_mode
    #         )
    #     count += 1
    # if not task.done():
    #     task.cancel()
    #     await update.message.reply_text(
    #         text=Messages.FIND_CONTINUE_STOP.value, parse_mode=settings.parse_mode
    #     )

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
