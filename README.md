# Mirage Userbot

## Установка

```bash
git clone https://github.com/the-phantom-git/mirage_userbot.git
cd mirage_userbot
pip install -r requirements.txt
```

## Настройка

В файлк main.py замените api_id и api_hash на свои:
```Python
app = Client(
    'main',
    api_id = ваш api_id,
    api_hash = ваш api_hash,
    plugins = dict(root='modules'),
)
```
А так же удалите эти строки кода:

```Python
from dotenv import load_dotenv
import os


load_dotenv()

api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')
```
ВАЖНО! Чтобы найти ваш api_id и api_hash нужно войти на сайте телеграма https://my.telegram.org/auth
Чтобы понять как получить api_id и api_hash на сайте, посмотрите пару видео в ютубе по запросу "api_id и api_hash как получить?"

```Python
api_id=your_api_id
api_hash=your_api_hash
```

## Запуск

```bash
python main.py
```