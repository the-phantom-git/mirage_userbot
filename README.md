# Mirage Userbot

Userbot на Pyrogram для Telegram.

---

# Требования

## 📱 Для телефона (Android)

* Установлен Termux (скачивать через F-Droid, НЕ из Google Play)

## 💻 Для компьютера

* Установлен Python (версия 3.10+)
* Установлен Git

---

# Установка

## 📱 Android (Termux)

Открываем Termux и по очереди вводим:

```bash
pkg update && pkg upgrade -y
pkg install python git -y
pip install --upgrade pip

git clone https://github.com/the-phantom-git/mirage_userbot.git
cd mirage_userbot

pip install pyrogram tgcrypto dotenv
```

---

## 💻 Компьютер (Windows / Linux)

Откройте терминал / PowerShell и введите:

```bash
git clone https://github.com/the-phantom-git/mirage_userbot.git
cd mirage_userbot

pip install pyrogram tgcrypto dotenv
```

---

# Настройка (Эти шаги для всех устройств)

## 1. Получение API данных

Переходим на сайт:
→ https://my.telegram.org/auth

Войдите в аккаунт и получите:

* `api_id`
* `api_hash`

(если не знаете как - просто загуглите: *"как получить api_id telegram"*)

---

## 2. Создание файла `.env`

В папке проекта создайте файл `.env`.

На телефоне вы должны быть в папке mirage_userbot:

```bash
nano .env
```

И вставьте туда:

```env
API_ID=ваш_api_id
API_HASH=ваш_api_hash
```

На телефоне после этого действия прожимаем ctrl + x → enter

---

# Запуск

```bash
python main.py
```

При первом запуске:

* введите номер телефона.
* введите код из Telegram.

После этого создастся `.session` файл и повторно вводить ничего не нужно.

---

# Обновление

Чтобы обновить бота до последней версии:

```bash
cd mirage_userbot
git pull
```

---

# Важно

* НЕ публикуйте файл `.env`.
* НЕ публикуйте `.session`.
* Если бот не запускается - проверьте, установлены ли зависимости.

---

# Полезно знать

* Бот работает только пока запущен.
* Для постоянной работы на телефоне используйте `tmux` в Termux (гуглим гуглим).
* Telegram может ограничивать частые действия (FloodWait).

---

# Поддержка

Если что-то не работает - проверьте шаги ещё раз.
В 90% случаев проблема в пропущенной команде или не том символе.
