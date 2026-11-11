from telethon import TelegramClient
from dotenv import load_dotenv
import os

load_dotenv()

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")

client = TelegramClient("my_session", api_id, api_hash)

async def main():
    me = await client.get_me()
    print("Il tuo Telegram User ID è:", me.id)

with client:
    client.loop.run_until_complete(main())