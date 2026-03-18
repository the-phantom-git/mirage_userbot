import asyncio
from pyrogram import Client, filters

_type_task: asyncio.Task | None = None


async def _typing_loop(msg, text: str, delay_ms: int):
    built = ''

    for ch in text:
        await msg.edit_text(built + '█')
        await asyncio.sleep(delay_ms / 1000)

        built += ch
        await msg.edit_text(built)

    print("[TYPE] Завершено")


@Client.on_message(filters.me & filters.command('type', '.'))
async def typing_animation(app: Client, msg):
    global _type_task

    print("[COMMAND] .type")

    args = msg.text.split()[1:]
    if not args:
        return await msg.edit_text("Использование: .type <текст> <задержка_мс>")

    delay_ms = 150
    if args[-1].isdigit():
        delay_ms = int(args[-1])
        args = args[:-1]

    text = ' '.join(args)

    if not text:
        return await msg.edit_text("Ошибка: текст не указан.")
    if delay_ms < 0:
        return await msg.edit_text("Ошибка: задержка должна быть положительной.")

    if _type_task and not _type_task.done():
        _type_task.cancel()
        await asyncio.sleep(0)
        print("[TYPE] Предыдущий процесс остановлен")

    await msg.edit_text("Запуск анимации печати...")

    _type_task = asyncio.create_task(_typing_loop(msg, text, delay_ms))


@Client.on_message(filters.me & filters.command('stoptype', '.'))
async def stop_typing(app: Client, msg):
    global _type_task

    print("[COMMAND] .stoptype")

    if _type_task and not _type_task.done():
        _type_task.cancel()
        await msg.reply("Процесс печати остановлен.")
    else:
        await msg.reply("Активный процесс отсутствует.")