from enum import Enum

from config import settings


class Messages(str, Enum):
    BOT_START_MESSAGE = 'Приложение на разработке'
    START_TRANSCRIBE = 'Присылай аудио для транскрибации'
    REPEAT_TRANSCRIBE = 'Присылай еще аудио для транскрибации'
    BOT_NOT_PERMIT = r'Приложение на разработке\.\.\.'
    EMPTY_TRANSCRIBE = 'В результате транскрибации текст не получен'


class Commands(Enum):
    START = 'start'
    TRANSCRIBE = 'transcribe'


class Buttons(str, Enum):
    PLACE_HOLDER = 'Жду файл'
    STOP = '\u21AA Выйти'


class BackendRoutes(str, Enum):
    TRANSCRIBATIONS = '/v1/audio/transcriptions'


class Differents(str, Enum):
    PHONE_NUMBER_FIELD = 'phone_number'


class Descriptions(str, Enum):
    PHONE = 'Телефонный номер'
