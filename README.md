# Описание проекта transcribator:
Сервис для транскрибирования речи. Построен по микросервисной архитектуре c применением брокера сообщений. Интерфейс взаимодействия с пользователем организован посредством телеграм бота, который принимает аудио сообщение от пользователя и сохраняет его на диск, после чего делает запрос на сервис `producer` о создании задания для транскрибирования. Сервис `producer` загружает задание в брокер сообщений, откуда они доставляются на сервис `consumer`, который уже отправляет ссылку на скаченный ранее файл в обработку в offline сервис `OpenAI`, а полученный текст направляет пользователю в телеграм. Для оптимального взаимодействия с api `telegram` и `producer` задействован шаблон проектирования `Прерыватель`. Дополнительно может осуществляется online перевод транскрибированного текста на русский язык с применением `Google Cloud Translation API`. При возникновении ошибок в Google api, текст возвращается без перевода. Поэтому в боте реализованы два режима: `Транскрибировать без перевода` и `Транскрибировать и перевести`.

### Используемые технологии:

Python 3.12, Fastapi, Python-telegram-bot, Docker, OpenAI, RabbitMQ.

### Как запустить проект:

```
cd /home/
git clone https://github.com/olegtsss/transcribator.git
cd transcribator
python3 -m venv venv
source venv/bin/activate
python3 -m pip install --upgrade pip
pip3 install -r docker/requirements_freeze.txt

python3 bot/main.py
python3 producer/main.py
python3 consumer/main.py
```

### Как запустить проект в Docker:

```
apt install docker docker-compose
cd /home/
git clone https://github.com/olegtsss/transcribator.git
cd transcribator/docker/
docker build -f Dockerfile_base -t transcribator_base_image .
docker-compose up -d --build
```

### Как обновить проект в Docker:

```
cd /home/spektr/docker/transcribator
docker-compose down
git pull
docker-compose up -d --build
```

## Шаблон наполнения env-файла:

```
LOG_LEVEL=DEBUG

PROXY_HOST=127.0.0.1
PROXY_WHISPER_PORT=8000
PROXY_PRODUCER_PORT=8001

PRODUCER_LISTENING_IP=127.0.0.1
PRODUCER_LISTENING_PORT=8001

TELEGRAM_BOT_TOKEN=
TELEGRAM_USERS=11111,22222

LOG_DIR=logs
LOG_BACKUP_COUNT=14
LOG_WHEN=midnight
LOG_INTERVAL=1
LOG_ENCODING=UTF-8

USER_AGENT=Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0

ROOT_TEMP_DIR=
```

### Просмотр логов:

```
tail -n 1000 /var/lib/docker/volumes/docker_logs_transcribator/_data/bot.log
tail -n 1000 /var/lib/docker/volumes/docker_logs_transcribator/_data/consumer.log
tail -n 1000 /var/lib/docker/volumes/docker_logs_transcribator/_data/producer.log
tail -n 1000 /var/lib/docker/volumes/docker_logs_transcribator/_data/uvicorn.log
docker logs --follow transcribator_whisper
docker logs --follow transcribator_bot
docker logs --follow transcribator_rabbit
docker logs --follow transcribator_producer
docker logs --follow transcribator_consumer
```

### Функциональное тестирование:

```
# docker/docker-compose.yml
-> transcribator_producer:
    ...
    ports:
      - 127.0.0.1:8001:8001

-> transcribator_rabbit:
    ...
    ports:
      - 127.0.0.1:5672:5672

-> transcribator_consumer:
  #   container_name: transcribator_consumer
  #   build:
  #     context: ../consumer/
  #     dockerfile: Dockerfile_consumer
  #   restart: always
  #   depends_on:
  #     - transcribator_rabbit
  #   env_file:
  #     - ../.env
  #   volumes:
  #     - logs_transcribator:/app/logs
  #     - temp_transcribator:/app/temp
  #   networks:
  #     app_net_3:
  #       ipv4_address: 10.0.2.7

pytest
```

### Разработчик:
[olegtsss](https://github.com/olegtsss)
[etalab-ia](https://github.com/etalab-ia/faster-whisper-server)

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=whte)
