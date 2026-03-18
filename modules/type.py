import asyncio
from pyrogram import Client, filters


_type_task: asyncio.Task | None = None


async def _typing_loop(app: Client, msg, text: str, delay_ms: int):

    built = ''
    for ch in text:
        await msg.edit_text(built + '#')
        await asyncio.sleep(delay_ms / 1000)

        built += ch
        await msg.edit_text(built)


@Client.on_message(filters.me & filters.command('type', '.'))
async def typing_animation(app: Client, msg):
    global _type_task

    args = msg.text.split()[1:]
    if not args:
        return await msg.edit_text('Использование: .type <сообщение> <задержка (мс)>')

    delay_ms = 150
    if args[-1].isdigit():
        delay_ms = int(args[-1])
        args = args[:-1]
    text = ' '.join(args)

    if not text:
        return await msg.edit_text('Сообщение не может быть пустым.')
    if delay_ms < 0:
        return await msg.edit_text('Задержка должна быть положительным числом.')

    if _type_task and not _type_task.done():
        _type_task.cancel()
        await asyncio.sleep(0)

    _type_task = asyncio.create_task(_typing_loop(app, msg, text, delay_ms))
    await msg.edit_text(f'Запущена печать: "{text}" (задержка {delay_ms} мс). Используйте .stoptype для остановки.')


@Client.on_message(filters.me & filters.command('stoptype', '.'))
async def stop_typing(app: Client, msg):
    global _type_task 
    if _type_task and not _type_task.done():
        _type_task.cancel()
        await msg.reply('Печать остановлена...')
    else:
        await msg.reply('В данный момент печать не запущена.')