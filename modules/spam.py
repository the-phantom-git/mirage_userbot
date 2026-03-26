import asyncio
import random
import time
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.errors import FloodWait

_spam_tasks = {}


def _format_time(seconds: int):
    return str(timedelta(seconds=int(seconds)))


def _generate_task_id():
    while True:
        task_id = str(random.randint(1, 9999))
        if task_id not in _spam_tasks:
            return task_id


def create_spam_task():
    task = {
        'task': None,
        'state': {
            'count': 0,
            'sent': 0,
            'start_time': None,
            'delay_ms': 0,
        },
        'pause_event': asyncio.Event(),
        'stop': False
    }
    task['pause_event'].set()
    return task


async def _spam_loop(app: Client, control_msg, text: str, task_data, task_id):
    state = task_data['state']
    state['start_time'] = time.time()

    next_pause_at = random.randint(15, 30)

    while state['sent'] < state['count']:

        if task_data['stop']:
            await control_msg.reply('[SPAM] Процесс остановлен.')
            return

        await task_data['pause_event'].wait()

        try:
            await app.send_message(control_msg.chat.id, text)
            state['sent'] += 1

            print(f'[SPAM] [ID: {task_id}] {state['sent']}/{state['count']}')

            base_delay = state['delay_ms'] / 1000
            await asyncio.sleep(random.uniform(base_delay * 0.7, base_delay * 1.8))

            if state['sent'] == next_pause_at:
                pause = random.uniform(3, 10)
                await asyncio.sleep(pause)
                next_pause_at += random.randint(15, 25)

        except FloodWait as e:
            print(f'[SPAM] FloodWait {e.value} сек')
            await asyncio.sleep(e.value + 1)

        except Exception as e:
            await control_msg.reply(f'[SPAM] Ошибка: {e}')
            return

    await control_msg.reply(
        f'[SPAM] Процесс завершён. Отправлено сообщений: {state['sent']}'
    )


def _cleanup_tasks():
    for task_id in list(_spam_tasks):
        t = _spam_tasks[task_id]
        if t['task'] and t['task'].done():
            del _spam_tasks[task_id]


def _log_status_console():
    if not _spam_tasks:
        print('[SPAM] Нет активных процессов.')
        return

    print('\n[SPAM] АКТИВНЫЕ ПРОЦЕССЫ:\n')

    for task_id, t in _spam_tasks.items():
        state = t['state']

        sent = state['sent']
        total = state['count']
        start_time = state['start_time']

        if not start_time:
            print(f'[{task_id}] Инициализация...')
            continue

        now = time.time()
        elapsed = now - start_time

        speed = sent / elapsed if elapsed > 0 else 0
        remaining = total - sent
        eta = remaining / speed if speed > 0 else 0

        start_dt = datetime.fromtimestamp(start_time)
        end_dt = datetime.fromtimestamp(now + eta)

        status = 'ПАУЗА' if not t['pause_event'].is_set() else 'РАБОТАЕТ'

        print(
            f'  ID: [{task_id}]\n'
            f'  Статус: {status}\n'
            f'  Прогресс: {sent}/{total}\n'
            f'  Скорость: {speed:.2f} msg/sec\n'
            f'  Запущено в: {start_dt.strftime('%H:%M:%S')}\n'
            f'  Ожидаемое завершение в: {end_dt.strftime('%H:%M:%S')}\n'
            f'  Осталось: {_format_time(eta)}\n'
        )


async def _update_status_text(msg):
    if not _spam_tasks:
        return await msg.edit_text('[SPAM] Активный процесс отсутствует.')

    text = '[SPAM] Статус процессов:\n\n'

    for task_id, t in _spam_tasks.items():
        state = t['state']

        sent = state['sent']
        total = state['count']
        start_time = state['start_time']

        if not start_time:
            text += f'ID: {task_id}\nИнициализация...\n\n'
            continue

        now = time.time()
        elapsed = now - start_time

        speed = sent / elapsed if elapsed > 0 else 0
        remaining = total - sent
        eta = remaining / speed if speed > 0 else 0

        end_time = datetime.fromtimestamp(now + eta)
        start_dt = datetime.fromtimestamp(start_time)

        text += (
            f'ID: {task_id}\n'
            f'Статус процесса:\n\n'
            f'Прогресс: {sent}/{total}\n'
            f'Скорость: {speed:.2f} msg/sec\n'
            f'Запущено в: {start_dt.strftime('%H:%M:%S')}\n'
            f'Ожидаемое завершение в: {end_time.strftime('%H:%M:%S')}\n'
            f'Осталось: {_format_time(eta)}\n\n'
        )

    await msg.edit_text(text)


@Client.on_message(filters.me & filters.command('spam', '.'))
async def spam(app: Client, msg):
    args = msg.text.split()[1:]

    if len(args) < 3:
        return await msg.reply(
            '[SPAM] Использование:\n.spam <текст> <количество> <задержка_мс>'
        )

    try:
        count = int(args[-2])
        delay_ms = int(args[-1])
    except ValueError:
        return await msg.reply('[SPAM] Ошибка: число/задержка неверны.')

    text = ' '.join(args[:-2])

    task_id = _generate_task_id()
    task_data = create_spam_task()

    task_data['state']['count'] = count
    task_data['state']['delay_ms'] = delay_ms

    control_msg = await msg.reply(
        f'[SPAM] Запущен спам\nID: {task_id}\nСообщений: {count}'
    )

    task = asyncio.create_task(
        _spam_loop(app, control_msg, text, task_data, task_id)
    )

    task_data['task'] = task
    _spam_tasks[task_id] = task_data

    await msg.delete()


@Client.on_message(filters.me & filters.command('spamstatus', '.'))
async def spam_status(app: Client, msg):
    _cleanup_tasks()

    status_msg = await msg.edit_text('[SPAM] Получение статуса...')

    await _update_status_text(status_msg)
    _log_status_console()


@Client.on_message(filters.me & filters.command('spampause', '.'))
async def pause_spam(app: Client, msg):
    args = msg.text.split()[1:]

    if not args:
        for t in _spam_tasks.values():
            t['pause_event'].clear()
        return await msg.edit_text('[SPAM] Все процессы поставлены на паузу.')

    task_id = args[0]

    if task_id in _spam_tasks:
        _spam_tasks[task_id]['pause_event'].clear()
        await msg.edit_text(f'[SPAM] Пауза: {task_id}')
        print(f'[SPAM] Пауза: {task_id}')
    else:
        await msg.edit_text('[SPAM] ID не найден.')


@Client.on_message(filters.me & filters.command('spamunpause', '.'))
async def unpause_spam(app: Client, msg):
    args = msg.text.split()[1:]

    if not args:
        for t in _spam_tasks.values():
            t['pause_event'].set()
        return await msg.edit_text('[SPAM] Все процессы возобновлены.')

    task_id = args[0]

    if task_id in _spam_tasks:
        _spam_tasks[task_id]['pause_event'].set()
        await msg.edit_text(f'[SPAM] Возобновлено: {task_id}')
        print(f'[SPAM] Возобновлено: {task_id}')
    else:
        await msg.edit_text('[SPAM] ID не найден.')


@Client.on_message(filters.me & filters.command('spamstop', '.'))
async def stop_spam(app: Client, msg):
    args = msg.text.split()[1:]

    if not args:
        for t in _spam_tasks.values():
            t['stop'] = True
            if t['task']:
                t['task'].cancel()
        return await msg.edit_text('[SPAM] Все процессы остановлены.')

    task_id = args[0]

    if task_id in _spam_tasks:
        t = _spam_tasks[task_id]
        t['stop'] = True
        if t['task']:
            t['task'].cancel()

        await msg.edit_text(f'[SPAM] Остановлен: {task_id}')
        print(f'[SPAM] Остановлен: {task_id}')
    else:
        await msg.edit_text('[SPAM] ID не найден.')