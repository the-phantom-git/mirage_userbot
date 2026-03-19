import asyncio
import random
import time
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.errors import FloodWait

_spam_task: asyncio.Task | None = None
_spam_stop = False

_spam_state = {
    "count": 0,
    "sent": 0,
    "start_time": None,
    "delay_ms": 0,
    "status_msg": None
}


def _format_time(seconds: int):
    return str(timedelta(seconds=int(seconds)))


async def _spam_loop(app: Client, control_msg, text: str, count: int, delay_ms: int):
    global _spam_stop, _spam_state

    _spam_state["count"] = count
    _spam_state["sent"] = 0
    _spam_state["start_time"] = time.time()
    _spam_state["delay_ms"] = delay_ms

    while _spam_state["sent"] < count:
        if _spam_stop:
            await control_msg.reply("Процесс остановлен.")
            return

        try:
            await app.send_message(control_msg.chat.id, text)
            _spam_state["sent"] += 1

            print(f"[SPAM] {_spam_state['sent']}/{count}")

            base_delay = delay_ms / 1000
            await asyncio.sleep(random.uniform(base_delay * 0.7, base_delay * 1.8))

            if _spam_state["sent"] % random.randint(10, 20) == 0:
                pause = random.uniform(5, 10)
                print(f"[SPAM] Пауза {pause:.2f} сек")
                await asyncio.sleep(pause)

        except FloodWait as e:
            wait_time = e.value
            print(f"[SPAM] FloodWait: {wait_time}")
            await control_msg.reply(f"Ограничение Telegram. Ожидание {wait_time} сек.")
            await asyncio.sleep(wait_time + 1)

        except Exception as e:
            print(f"[SPAM ERROR] {e}")
            await control_msg.reply(f"Ошибка: {e}")
            return

    await control_msg.reply(
        f"Процесс завершён. Отправлено сообщений: {_spam_state['sent']}"
    )


@Client.on_message(filters.me & filters.command("spam", "."))
async def spam(app: Client, msg):
    global _spam_task, _spam_stop, _spam_state

    print("[COMMAND] .spam")

    args = msg.text.split()[1:]

    if len(args) < 3:
        return await msg.reply(
            "Использование:\n.spam <текст> <количество> <задержка_мс>"
        )

    try:
        count = int(args[-2])
        delay_ms = int(args[-1])
    except ValueError:
        return await msg.reply("Ошибка: количество и задержка должны быть числами.")

    text = " ".join(args[:-2])

    if not text:
        return await msg.reply("Ошибка: текст сообщения не указан.")

    if _spam_task and not _spam_task.done():
        _spam_stop = True
        _spam_task.cancel()
        await asyncio.sleep(0)

    _spam_stop = False

    await msg.edit_text("Запуск процесса отправки сообщений...")

    _spam_state["status_msg"] = msg

    control_msg = await msg.reply(
        f"Процесс запущен.\nСообщений: {count}\nЗадержка: {delay_ms} мс"
    )

    _spam_task = asyncio.create_task(
        _spam_loop(app, control_msg, text, count, delay_ms)
    )


@Client.on_message(filters.me & filters.command("spamstatus", "."))
async def spam_status(app: Client, msg):
    global _spam_task, _spam_state

    print("[COMMAND] .spamstatus")

    status_msg = _spam_state.get("status_msg")

    if not status_msg:
        return await msg.reply("Ошибка: сообщение статуса не найдено.")

    if not _spam_task:
        return await status_msg.edit_text("Статус: процесс не запускался.")

    if _spam_task.done():
        return await status_msg.edit_text("Статус: процесс завершён.")

    sent = _spam_state["sent"]
    total = _spam_state["count"]
    start_time = _spam_state["start_time"]

    if not start_time:
        return await status_msg.edit_text("Статус: инициализация...")

    now = time.time()
    elapsed = now - start_time

    speed = sent / elapsed if elapsed > 0 else 0

    remaining = total - sent
    eta_seconds = remaining / speed if speed > 0 else 0

    end_time = datetime.fromtimestamp(now + eta_seconds)
    start_dt = datetime.fromtimestamp(start_time)

    try:
        await status_msg.edit_text(
            "Статус процесса:\n\n"
            f"Отправлено: {sent}/{total}\n"
            f"Скорость: {speed:.2f} msg/sec\n\n"
            f"Запущено: {start_dt.strftime('%H:%M:%S')}\n"
            f"Ожидаемое завершение: {end_time.strftime('%H:%M:%S')}\n\n"
            f"Осталось: {_format_time(eta_seconds)}"
        )
    except Exception as e:
        print(f"[STATUS ERROR] {e}")


@Client.on_message(filters.me & filters.command("stopspam", "."))
async def stop_spam(app: Client, msg):
    global _spam_task, _spam_stop

    print("[COMMAND] .stopspam")

    if _spam_task and not _spam_task.done():
        _spam_stop = True
        _spam_task.cancel()
        await msg.edit_text("Процесс остановлен.")
    else:
        await msg.reply("Активный процесс отсутствует.")