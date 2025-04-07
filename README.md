# Описание проекта transcribator:
Сервис для

### Используемые технологии:

Python 3.12, Fastapi, Python-telegram-bot, Docker.

### Архитектура проекта:

- 
# https://github.com/etalab-ia/faster-whisper-server

### Как запустить проект:

```
cd /home/
git clone https://github.com/olegtsss/transcribator.git
cd transcribator
python3 -m venv venv
source venv/bin/activate
python3 -m pip install --upgrade pip
pip3 install -r docker/requirements_freeze.txt

python3 backend/main.py
python3 bot/main.py
```

### Как запустить проект в Docker:

```
apt install docker docker-compose
cd /home/
git clone https://github.com/olegtsss/transcribator.git
cd transcribator/docker/
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

```

### Просмотр логов:

```
tail -n 1000 /var/lib/docker/volumes/docker_logs_transcribator/_data/bot.log

docker logs --follow transcribator_bot
```

### Примеры raw запросов к backend:


### Разработчик:
[olegtsss](https://github.com/olegtsss)
[etalab-ia](https://github.com/etalab-ia/faster-whisper-server)

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=whte)
