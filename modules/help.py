from pyrogram import Client, filters

_COMMANDS = {
    'Основные': ['.help', '.instruction'],
    'Анимация ввода': ['.type', '.typestop'],
    'Спам': ['.spam', '.spamstatus', '.spampause', '.spamunpause', '.spamstop'],
    'Калькулятор': ['.calc', '.calcr', '.calcres', '.calcresr', '.calcavg', '.calcavgr'],
}

_BRIEF = {
    'help': 'Список команд и краткая справка по ним.',
    'instruction': 'Полная инструкция по конкретной команде.',
    'type': 'Показывает анимацию печати текста.',
    'typestop': 'Останавливает анимацию печати.',
    'spam': 'Запускает спам-процесс с собственным ID.',
    'spamstatus': 'Показывает статус всех активных спам-процессов.',
    'spampause': 'Ставит на паузу один или все спам-процессы.',
    'spamunpause': 'Возобновляет один или все спам-процессы.',
    'spamstop': 'Останавливает один или все спам-процессы.',
    'calc': 'Считает выражение и показывает результат вместе с выражением.',
    'calcr': 'Как .calc, но округляет результат до 2 знаков.',
    'calcres': 'Показывает только результат выражения.',
    'calcresr': 'Как .calcres, но округляет результат до 2 знаков.',
    'calcavg': 'Вычисляет среднее значение списка чисел.',
    'calcavgr': 'Как .calcavg, но округляет результат до 2 знаков.',
}

_INSTRUCTIONS = {
    'help': 'Команда .help показывает список доступных команд.\nДля краткой справки используйте .help <команда>.\nДля полной инструкции используйте .instruction <команда>.',
    'instruction': 'Команда .instruction выводит полную инструкцию по нужной команде.\nПример: .instruction .spam',
    'type': 'Команда .type показывает текст посимвольно, имитируя печать.\nПример: .type Привет',
    'typestop': 'Команда .typestop останавливает текущую анимацию печати.',
    'spam': 'Команда .spam запускает спам.\nФормат: .spam <текст> <количество> <задержка_мс>.\nПример: .spam Привет 10 1500.\nКаждый процесс получает свой ID и управляется отдельно.',
    'spamstatus': 'Команда .spamstatus показывает статус всех активных спам-процессов.\nВыводит ID, прогресс, среднюю задержку, состояние и оставшееся время.',
    'spampause': 'Команда .spampause ставит на паузу процесс.\nФормат: .spampause [ID].\nЕсли ID не указан, пауза применяется ко всем процессам.',
    'spamunpause': 'Команда .spamunpause возобновляет процесс.\nФормат: .spamunpause [ID].\nЕсли ID не указан, возобновляются все процессы.',
    'spamstop': 'Команда .spamstop останавливает процесс.\nФормат: .spamstop [ID].\nЕсли ID не указан, останавливаются все процессы.',
    'calc': 'Команда .calc вычисляет выражение и показывает его вместе с результатом.\nПоддерживаются: (), +, -, *, /, **, %, //, sqrt(), root(), abs(), round(), pow(), avg(), pi, e.\nПример: .calc (2 / 2) * 4 ** 2',
    'calcr': 'Команда .calcr работает как .calc, но округляет результат до 2 знаков.\nПример: .calcr 10 / 3',
    'calcres': 'Команда .calcres выводит только числовой результат выражения.\nПример: .calcres 2 + 2',
    'calcresr': 'Команда .calcresr работает как .calcres, но округляет результат до 2 знаков.\nПример: .calcresr 10 / 3',
    'calcavg': 'Команда .calcavg вычисляет среднее значение списка чисел.\nПример: .calcavg 10 20 30',
    'calcavgr': 'Команда .calcavgr работает как .calcavg, но округляет результат до 2 знаков.\nПример: .calcavgr 10 20 30',
}

def _normalize_command(name: str) -> str:
    return name.lstrip('.').lower()

@Client.on_message(filters.me & filters.command('help', '.'))
async def help_command(app: Client, msg):
    args = msg.text.split()[1:]
    args_text = ' '.join(args)
    if args:
        print(f"[HELP] .help {args_text}")
    else:
        print('[COMMAND] .help')

    if args:
        cmd = _normalize_command(args[0])
        text = _BRIEF.get(cmd)
        if not text:
            return await msg.edit_text(f'[HELP] Команда не найдена: {args[0]}')
        return await msg.edit_text(f'[HELP] {args[0]}: {text}')

    lines = ['[HELP] Список доступных команд:']
    for group, cmds in _COMMANDS.items():
        lines.append(group + ': ' + ', '.join(cmds))
    lines.append('Для подробностей: .help <команда>')
    lines.append('Для полной инструкции: .instruction <команда>')

    await msg.edit_text('\n'.join(lines))

@Client.on_message(filters.me & filters.command('instruction', '.'))
async def instruction_command(app: Client, msg):
    args = msg.text.split()[1:]
    args_text = ' '.join(args)
    if args:
        print(f"[INSTRUCTION] .instruction {args_text}")
    else:
        print('[COMMAND] .instruction')
    if not args:
        return await msg.edit_text('[INSTRUCTION] Использование: .instruction <команда>')

    cmd = _normalize_command(args[0])
    text = _INSTRUCTIONS.get(cmd)
    if not text:
        return await msg.edit_text(f'[INSTRUCTION] Инструкция не найдена: {args[0]}')

    await msg.edit_text(f'[INSTRUCTION] {text}')