import ast
import math
import operator
import re

from pyrogram import Client, filters

_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv,
}

_ALLOWED_UNARY = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}

def _root(*args):
    if len(args) == 1:
        return args[0] ** 0.5
    if len(args) == 2:
        degree, value = args
        return value ** (1 / degree)
    raise ValueError('root() принимает 1 или 2 аргумента')

_ALLOWED_FUNCTIONS = {
    'sqrt': math.sqrt,
    'abs': abs,
    'round': round,
    'pow': pow,
    'root': _root,
    'avg': lambda *values: sum(values) / len(values) if values else float('nan'),
}

_ALLOWED_NAMES = {
    'pi': math.pi,
    'e': math.e,
}


def _eval_node(node):
    if isinstance(node, ast.Expression):
        return _eval_node(node.body)

    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError('Недопустимый литерал')

    if isinstance(node, ast.Num):
        return node.n

    if isinstance(node, ast.BinOp):
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        op_type = type(node.op)
        if op_type in _ALLOWED_OPERATORS:
            return _ALLOWED_OPERATORS[op_type](left, right)
        raise ValueError('Недопустимая операция')

    if isinstance(node, ast.UnaryOp):
        operand = _eval_node(node.operand)
        op_type = type(node.op)
        if op_type in _ALLOWED_UNARY:
            return _ALLOWED_UNARY[op_type](operand)
        raise ValueError('Недопустимый оператор')

    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ValueError('Недопустимый вызов функции')

        func_name = node.func.id
        if func_name not in _ALLOWED_FUNCTIONS:
            raise ValueError(f'Функция {func_name} не поддерживается')

        args = [_eval_node(arg) for arg in node.args]
        return _ALLOWED_FUNCTIONS[func_name](*args)

    if isinstance(node, ast.Name):
        if node.id in _ALLOWED_NAMES:
            return _ALLOWED_NAMES[node.id]
        raise ValueError(f'Имя {node.id} не поддерживается')

    if isinstance(node, ast.Tuple):
        return tuple(_eval_node(item) for item in node.elts)

    raise ValueError('Недопустимое выражение')


def _safe_eval(expression: str):
    expression = expression.replace('^', '**')
    tree = ast.parse(expression, mode='eval')
    return _eval_node(tree)


def _format_result(value, round_digits=None):
    if isinstance(value, bool):
        return str(value)

    if isinstance(value, float):
        if round_digits is not None:
            return f'{value:.2f}'
        if value.is_integer():
            return str(int(value))
        return format(value, '.15g')

    return str(value)


def _parse_number_list(text: str):
    if not text.strip():
        return []

    parts = re.split(r'[;,\s]+', text.strip())
    values = []
    for part in parts:
        if not part:
            continue
        values.append(float(part))
    return values


@Client.on_message(filters.me & filters.command(['calc', 'calcr'], '.'))
async def calc(app: Client, msg):
    command = msg.text.split()[0][1:]
    print(f'[COMMAND] .{command}')

    args = msg.text.split()[1:]
    if not args:
        return await msg.edit_text('Использование: .calc <выражение>')

    expression = ' '.join(args)
    try:
        result = _safe_eval(expression)
    except Exception as e:
        return await msg.edit_text(f'[CALC] Ошибка: {e}')

    round_digits = 2 if command.endswith('r') else None
    await msg.edit_text(
        f'[CALC] `{expression} = {_format_result(result, round_digits)}`',
        parse_mode=None
    )


@Client.on_message(filters.me & filters.command(['calcres', 'calcresr'], '.'))
async def calc_res(app: Client, msg):
    command = msg.text.split()[0][1:]
    print(f'[COMMAND] .{command}')

    args = msg.text.split()[1:]
    if not args:
        return await msg.edit_text('Использование: .calcres <выражение>')

    expression = ' '.join(args)
    try:
        result = _safe_eval(expression)
    except Exception as e:
        return await msg.edit_text(f'[CALC] Ошибка: {e}')

    round_digits = 2 if command.endswith('r') else None
    await msg.edit_text(f'[CALC] {_format_result(result, round_digits)}')


@Client.on_message(filters.me & filters.command(['calcavg', 'calcavgr'], '.'))
async def calc_avg(app: Client, msg):
    command = msg.text.split()[0][1:]
    print(f'[COMMAND] .{command}')

    args = msg.text.split()[1:]
    if not args:
        return await msg.edit_text('Использование: .calcavg <число1> <число2> ...')

    values = _parse_number_list(' '.join(args))
    if not values:
        return await msg.edit_text('Ошибка: не удалось распознать числа.')

    average = sum(values) / len(values)
    round_digits = 2 if command.endswith('r') else None
    await msg.edit_text(
        f'[CALCAVG] Среднее значение: {_format_result(average, round_digits)}\n'
        f'Числа: {", ".join(str(v) for v in values)}'
    )