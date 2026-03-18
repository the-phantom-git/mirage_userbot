from datetime import datetime, timedelta
from pyrogram import Client, filters


def _parse_duration(tokens):
    if len(tokens) < 2:
        return None, tokens

    try:
        num = int(tokens[-2])
    except ValueError:
        return None, tokens

    unit = tokens[-1].lower()

    if unit in ('ч', 'час', 'часа', 'часов'):
        return timedelta(hours=num), tokens[:-2]

    if unit in ('м', 'мин', 'минута', 'минут', 'минуты'):
        return timedelta(minutes=num), tokens[:-2]

    if unit in ('д', 'день', 'дня', 'дней'):
        return timedelta(days=num), tokens[:-2]

    return None, tokens


def _sender(m):
    if not m.from_user:
        return None

    if m.from_user.username:
        return f'@{m.from_user.username}'

    name = f'{m.from_user.first_name or ""} {m.from_user.last_name or ""}'.strip()
    return name if name else f'id{m.from_user.id}'


def _format(m, text):
    sender = _sender(m)
    if not sender:
        return None

    time = m.date.strftime('%d.%m.%Y %H:%M')
    snippet = text.replace('\n', ' ')

    if len(snippet) > 120:
        snippet = snippet[:117] + '...'

    return f'{sender} | {time}: {snippet}'


@Client.on_message(filters.me & filters.command('search', '.'))
async def search(app: Client, msg):
    print("[COMMAND] .search")

    args = msg.text.split()[1:]
    if not args:
        return await msg.reply("Ошибка: укажите текст для поиска.")

    duration, args = _parse_duration(args)
    if duration is None:
        duration = timedelta(days=3650)

    query = ' '.join(args)
    oldest = datetime.utcnow() - duration

    status = await msg.reply("Поиск запущен...")

    results = []

    async for m in app.search_messages(msg.chat.id, query=query, limit=100):
        if not m.date or m.date < oldest:
            continue

        text = m.text or m.caption
        if not text:
            continue

        formatted = _format(m, text)
        if formatted:
            results.append(formatted)

        if len(results) >= 15:
            break

    if not results:
        return await status.edit_text("Результаты не найдены.")

    await status.edit_text("\n".join(results))


@Client.on_message(filters.me & filters.command('searchdeep', '.'))
async def search_deep(app: Client, msg):
    print("[COMMAND] .searchdeep")

    args = msg.text.split()[1:]
    if not args:
        return await msg.reply("Ошибка: укажите текст для поиска.")

    duration, args = _parse_duration(args)
    if duration is None:
        duration = timedelta(days=3650)

    query = ' '.join(args).lower()
    oldest = datetime.utcnow() - duration

    status = await msg.reply("Глубокий поиск запущен...")

    results = []

    async for m in app.get_chat_history(msg.chat.id, limit=100):
        if not m.date or m.date < oldest:
            break

        text = m.text or m.caption
        if not text or query not in text.lower():
            continue

        formatted = _format(m, text)
        if formatted:
            results.append(formatted)

        if len(results) >= 15:
            break

    if not results:
        return await status.edit_text("Результаты не найдены.")

    await status.edit_text("\n".join(results))