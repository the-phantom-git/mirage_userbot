import asyncio
import random
from pyrogram import Client, filters
from pyrogram.errors import FloodWait

_spam_task: asyncio.Task | None = None
_spam_stop = False


async def _spam_loop(app: Client, control_msg, text: str, count: int, delay_ms: int):
    global _spam_stop

    sent = 0

    while sent < count:
        if _spam_stop:
            await control_msg.reply("Процесс остановлен.")
            return

        try:
            await app.send_message(control_msg.chat.id, text)
            sent += 1

            print(f"[SPAM] {sent}/{count}")

            base_delay = delay_ms / 1000
            await asyncio.sleep(random.uniform(base_delay * 0.7, base_delay * 1.8))

            if sent % random.randint(10, 20) == 0:
                pause = random.uniform(5, 15)
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

    await control_msg.reply(f"Процесс завершён. Отправлено сообщений: {sent}")


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


@Client.on_message(filters.me & filters.command("stopspam", "."))
async def stop_spam(app: Client, msg):
    global _spam_task, _spam_stop

    print("[COMMAND] .stopspam")

    if _spam_task and not _spam_task.done():
        _spam_stop = True
        _spam_task.cancel()
        await msg.reply("Остановка процесса...")
    else:
        await msg.reply("Активный процесс отсутствует.")