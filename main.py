from pyrogram import Client, filters
from dotenv import load_dotenv
import os


load_dotenv()

api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')


app = Client(
    'main',
    api_id = api_id,
    api_hash = api_hash,
    plugins = dict(root='modules'),
)


if __name__ == '__main__':
    print('Mirage has been activated.')
    try:
        app.run()
    except KeyboardInterrupt:
        print('Mirage was stopped in console.')