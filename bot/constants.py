from enum import Enum


class Messages(str, Enum):
    BOT_START_MESSAGE = 'Для работы с ботом необходимо связаться с администратором'
    BOT_START_MESSAGE_LOG = 'Старт диалога с telegram_id=%s %s'
    START_TRANSCRIBE = 'Присылай аудио для транскрибации'
    REPEAT_TRANSCRIBE = 'Присылай еще аудио для транскрибации'
    BOT_NOT_PERMIT = r'Приложение на разработке\.\.\.'
    EMPTY_TRANSCRIBE = 'В результате транскрибации текст не получен'
    PRINT_BUTTONS = 'Получен запрос на показ меню от %s'
    AUDIO_RECEIVE = 'Получен аудио файл от %s'
    AUDIO_DOWNLOAD = 'Аудио файл сохранен: %s'
    AUDIO_DELETE = 'Аудио файл удален: %s'
    FILE_VERY_BIG = r'Полученный файл очень большой, обработка отклонена\.'


class Commands(Enum):
    START = 'start'
    TRANSCRIBE = 'transcribe'


class Buttons(str, Enum):
    PLACE_HOLDER = 'Жду файл'
    STOP = '\u21AA Выйти'
