from telethon import TelegramClient, sync, events    # events serve
from telethon.tl.functions.messages import GetStickerSetRequest
from telethon.tl.types import InputStickerSetShortName, MessageMediaDocument, DocumentAttributeSticker   # questi dovrebbero servire
import os
from dotenv import load_dotenv

load_dotenv()  # Carica le variabili da .env

# accesso alle variabili
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")

client = TelegramClient('session_sticker_id', api_id, api_hash)

@client.on(events.NewMessage())
async def sticker_handler(event):
    # controllo che il messaggio contenga sticker
    if isinstance(event.message.media, MessageMediaDocument):
        print('debug2')
        if event.message.sticker:  # Controllo specifico
            sticker = event.message.document
            print(f"Sticker ID: {sticker.id}")
            print(f"Sticker Set ID: {sticker.attributes[1].stickerset.id}")
            print(f"Sticker Set Access Hash: {sticker.attributes[1].stickerset.access_hash}")
            
            # controllo dell'attributo emoji nello sticker
            emoji = None
            for attr in sticker.attributes:
                if isinstance(attr, DocumentAttributeSticker):
                    emoji = attr.alt 
                    break

            if emoji:
                print(f"Emoji sticker: {emoji}")
            else:
                print("nessun emoji per questo sticker")

async def main():
    await client.start(bot_token=bot_token)
    print("Bot connesso...")

with client:
    client.loop.run_until_complete(main())
    client.run_until_disconnected() 