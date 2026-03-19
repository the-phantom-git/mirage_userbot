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
    "status_view_msg": None
}


def _format_time(seconds: int):
    return str(timedelta(seconds=int(seconds)))


async def _update_status_text():
    global _spam_task, _spam_state

    status_msg = _spam_state.get("status_view_msg")
    if not status_msg:
        return

    sent = _spam_state["sent"]
    total = _spam_state["count"]
    start_time = _spam_state["start_time"]

    if _spam_task and _spam_task.done():
        try:
            return await status_msg.edit_text(
                "Статус процесса:\n\n"
                f"Отправлено: {sent}/{total}\n\n"
                "Состояние: завершён"
            )
        except Exception as e:
            print(f"[STATUS ERROR] {e}")
        return

    if not start_time:
        return await status_msg.edit_text("Статус: инициализация...")

    now = time.time()
    elapsed = now - start_time

    speed = sent / elapsed if elapsed > 0 else 0
    remaining = total - sent
    eta = remaining / speed if speed > 0 else 0

    end_time = datetime.fromtimestamp(now + eta)
    start_dt = datetime.fromtimestamp(start_time)

    try:
        await status_msg.edit_text(
            "Статус процесса:\n\n"
            f"Отправлено: {sent}/{total}\n"
            f"Скорость: {speed:.2f} msg/sec\n\n"
            f"Запущено: {start_dt.strftime('%H:%M:%S')}\n"
            f"Ожидаемое завершение: {end_time.strftime('%H:%M:%S')}\n\n"
            f"Осталось: {_format_time(eta)}"
        )
    except Exception as e:
        print(f"[STATUS ERROR] {e}")


async def _spam_loop(app: Client, control_msg, text: str, count: int, delay_ms: int):
    global _spam_stop, _spam_state

    _spam_state["count"] = count
    _spam_state["sent"] = 0
    _spam_state["start_time"] = time.time()
    _spam_state["delay_ms"] = delay_ms

    while _spam_state["sent"] < count:
        if _spam_stop:
            await control_msg.reply("Процесс остановлен.")
            await _update_status_text()
            return

        try:
            await app.send_message(control_msg.chat.id, text)
            _spam_state["sent"] += 1

            print(f"[SPAM] {_spam_state['sent']}/{count}")

            base_delay = delay_ms / 1000
            await asyncio.sleep(random.uniform(base_delay * 0.7, base_delay * 1.8))

            if _spam_state["sent"] % random.randint(10, 20) == 0:
                pause = random.uniform(5, 10)
                await asyncio.sleep(pause)

        except FloodWait as e:
            await control_msg.reply(f"Ограничение Telegram. Ожидание {e.value} сек.")
            await asyncio.sleep(e.value + 1)

        except Exception as e:
            await control_msg.reply(f"Ошибка: {e}")
            return

    await control_msg.reply(
        f"Процесс завершён. Отправлено сообщений: {_spam_state['sent']}"
    )

    await _update_status_text()


@Client.on_message(filters.me & filters.command("spam", "."))
async def spam(app: Client, msg):
    global _spam_task, _spam_stop

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

    control_msg = await msg.reply(
        f"Процесс запущен.\nСообщений: {count}\nЗадержка: {delay_ms} мс"
    )

    _spam_task = asyncio.create_task(
        _spam_loop(app, control_msg, text, count, delay_ms)
    )


@Client.on_message(filters.me & filters.command("spamstatus", "."))
async def spam_status(app: Client, msg):
    global _spam_state

    print("[COMMAND] .spamstatus")

    if _spam_state.get("status_view_msg"):
        try:
            await _spam_state["status_view_msg"].edit_text(
                "Статус устарел."
            )
        except:
            pass

    status_msg = await msg.edit_text("Получение статуса...")

    _spam_state["status_view_msg"] = status_msg

    await _update_status_text()


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