import time
from typing import Dict, List, Any
from pyrogram.errors import FloodWait
from pyrogram import Client, filters
import functools
import asyncio

class BotStats:
    def __init__(self):
        self.start_time = time.time()
        self.command_counts: Dict[str, int] = {}
        self.error_counts: Dict[str, int] = {}
        self.error_details: List[Dict[str, Any]] = []
        self.flood_wait_count = 0
        self.flood_wait_total_time = 0

    def increment_command(self, command: str):
        self.command_counts[command] = self.command_counts.get(command, 0) + 1

    def add_error(self, error_type: str, command: str = None, details: str = None):
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        self.error_details.append({
            'time': time.time(),
            'error_type': error_type,
            'command': command,
            'details': details
        })

    def add_flood_wait(self, wait_time: int, command: str = None):
        self.flood_wait_count += 1
        self.flood_wait_total_time += wait_time
        self.add_error('FloodWait', command, f'Wait time: {wait_time}s')

    def get_uptime(self) -> str:
        uptime = time.time() - self.start_time
        hours, remainder = divmod(int(uptime), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def get_start_time(self) -> str:
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.start_time))

    def get_command_stats(self) -> str:
        if not self.command_counts:
            return "Команды не вызывались."
        stats = "\n".join(f"{cmd}: {count} раз" for cmd, count in self.command_counts.items())
        return f"Вызовы команд:\n{stats}"

    def get_error_stats(self) -> str:
        if not self.error_counts:
            return "С момента запуска бота ошибок не было."
        stats = "\n".join(f"{err}: {count} раз" for err, count in self.error_counts.items())
        if 'FloodWait' in self.error_counts:
            stats += f"\nFloodWait - {self.flood_wait_count} times | общее время {self.flood_wait_total_time} сек."
        return f"Errors:\n{stats}"

    def get_error_details(self) -> str:
        if not self.error_details:
            return "Деталей ошибок нет."
        details = []
        for err in self.error_details[-30:]: 
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(err['time']))
            cmd = err['command'] or 'N/A'
            details.append(f"{timestamp} - {err['error_type']} в {cmd}: {err['details'] or 'N/A'}")
        return "Последние ошибки:\n" + "\n".join(details)


stats = BotStats()

def command_handler():
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(client: Client, message, *args, **kwargs):
            command = message.text.split()[0][1:] if message.text else 'unknown'
            stats.increment_command(command)
            try:
                return await func(client, message, *args, **kwargs)
            except FloodWait as e:
                stats.add_flood_wait(e.value, command)
                await message.reply(f"FloodWait: ждем {e.value} секунд.")
                await asyncio.sleep(e.value)
            except Exception as e:
                error_type = type(e).__name__
                stats.add_error(error_type, command, str(e))
                await message.reply(f"Ошибка в {command}: {error_type} - {str(e)}")
        return wrapper
    return decorator

@Client.on_message(filters.me & filters.command(['status', 'statuserrors', 'statuscommands', 'statusuptime', 'statusall'], '.'))
@command_handler()
async def status_command(app: Client, msg):
    command = msg.text.split()[0][1:].lower() if msg.text else 'status'
    args = msg.text.split()[1:]
    first_arg = args[0].lower() if args else ''

    if command == 'statuserrors':
        if first_arg in ('detail', 'details'):
            await msg.edit_text(stats.get_error_details())
            return
        await msg.edit_text(stats.get_error_stats())
        return

    if command == 'statuscommands':
        await msg.edit_text(stats.get_command_stats())
        return

    if command == 'statusuptime':
        await msg.edit_text(f"Бот работает: {stats.get_uptime()}")
        return

    if command == 'statusall':
        command = 'status'

    if command == 'status':
        if first_arg in ('errors', 'error'):
            if len(args) > 1 and args[1].lower() in ('detail', 'details'):
                await msg.edit_text(stats.get_error_details())
            else:
                await msg.edit_text(stats.get_error_stats())
            return

        if first_arg in ('commands', 'cmds'):
            await msg.edit_text(stats.get_command_stats())
            return

        if first_arg == 'uptime':
            await msg.edit_text(f"Бот работает: {stats.get_uptime()}\nЗапущен: {stats.get_start_time()}")
            return

        uptime = stats.get_uptime()
        cmd_stats = stats.get_command_stats()
        err_stats = stats.get_error_stats()
        response = f"Бот работает: {uptime}\nЗапущен: {stats.get_start_time()}\n\n{cmd_stats}\n\n{err_stats}"
        await msg.edit_text(response)
        return

    await msg.edit_text('[STATUS] Неизвестная подкоманда. Использование:\n.status, .status uptime, .status commands, .status errors, .status errors detail')