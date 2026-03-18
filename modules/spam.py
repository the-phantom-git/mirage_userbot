import asyncio
from pyrogram import Client, filters


_spam_task: asyncio.Task | None = None
_spam_stop = False


async def _spam_loop(app: Client, msg, text: str, count: int, delay_ms: int):
    global _spam_stop

    for i in range(count):
        if _spam_stop:
            await msg.edit_text('Спам остановлен.')
            return
        try:
            await app.send_message(msg.chat.id, text)
        except Exception as e:
            await msg.reply(f'Ошибка при отправке сообщения: {e}')
            return
        if i != count - 1:
            await asyncio.sleep(delay_ms / 1000)
    await msg.reply('Спам завершён.')


@Client.on_message(filters.me & filters.command('spam', ','))
async def spam(app: Client, msg):
    global _spam_task, _spam_stop
    args = msg.text.split()[1:]
    if len(args) < 3:
        return await msg.reply('Использование: .spam <сообщение> <количество>\n<задержка (мс)>')
    try:
        count = int(args[-2])
        delay_ms = int(args[-1])
    except ValueError:
        return await msg.reply('Количество и задержка должны быть целыми числами.')
    text = ' '.join(args[:-2])
    if not text:
        return await msg.reply('Сообщение не может быть пустым.')
    if _spam_task and not _spam_task.done():
        _spam_stop = True
        _spam_task.cancel()
        await asyncio.sleep(0)
    _spam_stop = False
    _spam_task = asyncio.create_task(_spam_loop(app, msg, text, count, delay_ms))
    await msg.edit_text(f'Запущен спам: {count} сообщений с задержкой {delay_ms} мс.\nИспользуйте .stopspam для остановки')


@Client.on_message(filters.me & filters.command('stopspam', ','))
async def stop_spam(app: Client, msg):
    global _spam_task, _spam_stop
    if _spam_task and not _spam_task.done():
        _spam_stop = True
        _spam_task.cancel()
        await msg.reply('Спам остановлен...')
    else:
        await msg.reply('В данный момент спам не запущен..')