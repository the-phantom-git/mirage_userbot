from pyrogram import Client, filters


@Client.on_message(filters.me & filters.command('help', '.'))
async def help_command(app: Client, msg):
    print("[COMMAND] .help")

    await msg.reply(
        "Список доступных команд:\n\n"

        "Основные:\n"
        ".help — вывод данного сообщения\n\n"

        "Анимация текста:\n"
        ".type <текст> <задержка_мс>\n"
        ".stoptype — остановка анимации\n\n"

        "Спам:\n"
        ".spam <текст> <количество> <задержка_мс>\n"
        ".stopspam — остановка процесса\n\n"

        "Поиск:\n"
        ".search <текст> <время>\n"
        ".searchdeep <текст> <время>\n\n"

        "Примечание:\n"
        "Для применения изменений требуется перезапуск."
    )