from enum import Enum

APP_NAME: str = 'Consumer'


class Messanges(str, Enum):
    BACKEND_START = 'Приложение запущено'
    ERROR_FROM_EXTERNAL_API = 'При обращении к API возникла ошибка: %s'
    VALIDATION_ERROR = 'Полученная от брокера информация не прошла валидацию: %s'
    FILE_NOT_EXIST = 'Файл аудио не найден: %s'
    TRANSCRIPT_SUCCESS = 'Файл %s транскрибирован. Длина сообщения %s символов'
    AUDIO_DELETE = 'Файл удален %s'
    EMPTY_TRANSCRIBE = 'В результате транскрибации текст не получен'
    RETRY_ERROR = 'Во время запроса произошла ошибка (попытка %s), повторная попытка. Ошибка: %s'
    ANSWER = '{entity_id}:\n\n{text}'
    MESSAGE_DONT_SEND = 'Не удалось отправить сообщение пользователю %s: %s'
    MESSAGE_DONE = 'Сообщение готово к отправке: %s'
