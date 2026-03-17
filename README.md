# Mirage Userbot

## Установка

```bash
git update && pkg upgrade -y
pkg install python git -y
pip install --upgrade pip
git clone https://github.com/the-phantom-git/mirage_userbot.git
cd mirage_userbot
pip install pyrogram
pip install tgcrypto
pip install dotenv
```

## Настройка

ВАЖНО! Чтобы найти ваш api_id и api_hash нужно войти на сайте телеграма https://my.telegram.org/auth
Чтобы понять как получить api_id и api_hash на сайте, посмотрите пару видео в ютубе по запросу "api_id и api_hash как получить?"

Создайте файл .env и поместите туда ваши api_id api_hash:
```Python


API_ID=your_api_id
API_HASH=your_api_hash
```
## Обновление

cd mirage_userbot
git pull

## Запуск в консоль

```bash
python main.py
```
