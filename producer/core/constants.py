from enum import Enum


class Differents(str, Enum):
    DETAIL = 'detail'


class Messanges(str, Enum):
    BACKEND_START = 'Приложение запущено'
    SERVER_ERROR = 'Internal server error'
    TASK_CANCELED_FOR_TIMEOUT_COMMON = 'Задание отменено по таймауту, вызывалась функция %s'
    RECEIVE_DATA_FOR_PRODUCE = 'Получены данне для загрузки: %s'


class Descriptions(str, Enum):
    RABBIT = 'Загрузка данных в RabbitMQ'
    CREATE_TASK = 'Создать задание для транскрибации'
    HEALTH = 'Проверка отклика api для producer'
    TELEGRAM_ID = 'Telegram ID'
    PATH = 'Путь до файла'
