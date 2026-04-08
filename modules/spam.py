import asyncio
import random
import time
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.errors import FloodWait

_spam_tasks = {}


def _format_time(seconds: float):
    seconds = max(0, int(round(seconds)))
    return str(timedelta(seconds=seconds))


def _format_delay(delay_ms: int):
    seconds = delay_ms / 1000
    return f'{seconds:.1f}сек / {delay_ms}мс'


def _estimate_eta(remaining: int, delay_ms: int):
    if remaining <= 0:
        return 0.0

    avg_delay = delay_ms / 1000 * 1.25
    avg_pause_interval = 20
    avg_pause_duration = 6.5
    expected_pauses = (remaining + avg_pause_interval - 1) // avg_pause_interval

    return remaining * avg_delay + expected_pauses * avg_pause_duration


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

    next_pause_at = random.randint(15, 50)
    last_pause_at = 0

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
                pause = random.uniform(2, 8)

                if last_pause_at == 0:
                    print(f'[SPAM] [ID: {task_id}] Пауза: {pause:.2f} сек')
                else:
                    msgs_since_last_pause = state['sent'] - last_pause_at
                    print(f'[SPAM] [ID: {task_id}] Пауза: {pause:.2f} сек | С прошлой паузы: {msgs_since_last_pause}')

                    await asyncio.sleep(pause)

                last_pause_at = state['sent']
                next_pause_at += random.randint(15, 50)

        except FloodWait as e:
            print(f'[SPAM] [ID: {task_id}] FloodWait {e.value} сек')
            await asyncio.sleep(e.value + 1)

        except Exception as e:
            await control_msg.reply(f'[SPAM] [ID: {task_id}] Ошибка: {e}')
            return
    await control_msg.reply(f'[SPAM] Процесс завершён\nID: {task_id}\nОтправлено сообщений: {state['sent']}\nВремя: {_format_time(time.time() - state['start_time'])}')
    print(f'[SPAM] [ID: {task_id}] Процесс завершён.\n  Отправлено сообщений: {state['sent']}\n  Время: {_format_time(time.time() - state['start_time'])}')


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

        remaining = total - sent
        eta = _estimate_eta(remaining, state['delay_ms'])
        delay_info = _format_delay(state['delay_ms'])

        start_dt = datetime.fromtimestamp(start_time)
        end_dt = datetime.fromtimestamp(time.time() + eta)

        if sent >= total:
            status = 'Завершён'
        elif not t['pause_event'].is_set():
            status = 'Приостановлен'
        else:
            status = 'Работает'

        print(
            f'  ID: [{task_id}]\n'
            f'  Статус: {status}\n'
            f'  Прогресс: {sent}/{total}\n'
            f'  Средняя задержка: {delay_info}\n'
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

        remaining = total - sent
        eta = _estimate_eta(remaining, state['delay_ms'])
        delay_info = _format_delay(state['delay_ms'])

        end_time = datetime.fromtimestamp(time.time() + eta)
        start_dt = datetime.fromtimestamp(start_time)

        if sent >= total:
            status = 'Завершён'
        elif not t['pause_event'].is_set():
            status = 'Приостановлен'
        else:
            status = 'Работает'

        text += (
            f'ID: {task_id}\n'
            f'Статус: {status}\n'
            f'Прогресс: {sent}/{total}\n'
            f'Средняя задержка: {delay_info}\n'
            f'Запущено в: {start_dt.strftime('%H:%M:%S')}\n'
            f'Ожидаемое завершение в: {end_time.strftime('%H:%M:%S')}\n'
            f'Осталось: {_format_time(eta)}\n\n'
        )

    await msg.edit_text(text)


@Client.on_message(filters.me & filters.command('spam', '.'))
async def spam(app: Client, msg):
    print('[COMMAND] .spam')
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

    control_msg = await msg.edit_text(f'[SPAM] Запущен спам\nID: {task_id}\nСообщений: {count}\nЗадержка: {delay_ms} мс')
    print(f'[SPAM] Запущен спам\n  ID: {task_id}\n  Сообщений: {count}\n  Задержка: {delay_ms} мс')

    task = asyncio.create_task(
        _spam_loop(app, control_msg, text, task_data, task_id)
    )

    task_data['task'] = task
    _spam_tasks[task_id] = task_data


@Client.on_message(filters.me & filters.command('spamstatus', '.'))
async def spam_status(app: Client, msg):
    print('[COMMAND] .spamstatus')
    _cleanup_tasks()

    status_msg = await msg.edit_text('[SPAM] Получение статуса...')

    await _update_status_text(status_msg)
    _log_status_console()


@Client.on_message(filters.me & filters.command('spampause', '.'))
async def pause_spam(app: Client, msg):
    print('[COMMAND] .spampause')
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
    print('[COMMAND] .spamunpause')
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
    print('[COMMAND] .spamstop')
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