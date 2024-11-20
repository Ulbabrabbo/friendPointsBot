import sqlite3
from telethon import TelegramClient, sync, events    # events serve
from telethon.tl.functions.messages import GetStickerSetRequest
from telethon.tl.types import InputStickerSetShortName, MessageMediaDocument, DocumentAttributeSticker   # questi dovrebbero servire
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()  # Carica le variabili da .env

# accesso alle variabili
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")

client = TelegramClient('session_fp', api_id, api_hash)

# variabili per gli ID degli sticker
STICKER_ADD_100_ID = int(os.getenv('STICKER_ADD_100_ID'))    # Sticker ID per aggiungere 100 p
STICKER_SUB_100_ID = int(os.getenv('STICKER_SUB_100_ID'))    # Sticker ID per levare 100 p
AdminUserID = int(os.getenv('ADMIN_USER_ID'))

# parte di setup DB SQLite 
conn = sqlite3.connect('friend_points.db')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS points (
    user_id INTEGER,
    chat_id INTEGER,
    username TEXT,
    points INTEGER DEFAULT 0,
    PRIMARY KEY (user_id, chat_id)
)
''')
conn.commit()

# Funzione per modificare i punti dell'utente
def update_points(user_id, chat_id, username, points_delta):
    cursor.execute("SELECT points FROM points WHERE user_id = ? AND chat_id = ?", (user_id, chat_id))
    result = cursor.fetchone()
    if result:
        current_points = result[0]
        cursor.execute("UPDATE points SET points = ?, username = ? WHERE user_id = ? AND chat_id = ?", 
                       (current_points + points_delta, username, user_id, chat_id))
    else:
        cursor.execute("INSERT INTO points (user_id, chat_id, username, points) VALUES (?, ?, ?, ?)", 
                       (user_id, chat_id, username, points_delta))
    conn.commit()

# Funzione per mostrare la leaderboard
def get_leaderboard(chat_id):
    cursor.execute("SELECT username, points FROM points WHERE chat_id = ? ORDER BY points DESC", (chat_id,))
    leaderboard = cursor.fetchall()
    return leaderboard

# Funzione per resettare la tabella punteggi
def reset_points(chat_id):
    cursor.execute("DELETE FROM points WHERE chat_id = ?", (chat_id,))
    conn.commit()


# Funzione per gestire il comando /help
@client.on(events.NewMessage(pattern='/help'))
async def show_help(event):
    chat_id = event.chat_id
    delay_help = 15

    help_message = """Ciao! Sono FriendBot, il tuo bot per la gestione dei punti amicizia. Ecco cosa posso fare:
\n1. **Punti Amicizia tramite Sticker**
- Per aggiungere o togliere punti a qualcuno, rispondi a un messaggio con uno sticker specifico
- Se usi uno sticker **positivo** (aggiungi punti), l'utente riceverà dei punti amicizia.
- Se usi uno sticker **negativo** (togli punti), l'utente perderà dei punti amicizia.
- Ogni sticker ha un ID unico, e ogni gruppo ha il proprio set di sticker che può essere configurato per aggiungere o togliere punti.
\n2. **comando /leaderboard**
- Il comando `/leaderboard` mostra la classifica di tutti gli utenti della chat e i loro punti amicizia.
- I punti vengono visualizzati accanto all'ID dell'utente nella classifica.
\n3. **comando /reset**
- Il comando `/reset` resetta i punti di tutti gli utenti nel gruppo. Solo un amministratore può eseguire questa azione.
\nQuesti sono i comandi principali, se hai bisogno di aiuto, non esitare a chiedere!
\nA presto!"""
    
    # Invia il messaggio al gruppo o alla chat privata
    await send_and_delete_message(chat_id, event, help_message, delay_help)


# Funzione per gestire il comando /leaderboard
@client.on(events.NewMessage(pattern='/leaderboard'))
async def show_leaderboard(event):
    chat_id = event.chat_id
    delay_leaderboard = 5

    leaderboard = get_leaderboard(chat_id)
    if leaderboard:
        leaderboard_message = "\n".join([f"{username}: {points} points" for username, points in leaderboard])
    else:
        leaderboard_message = "La leaderboard è vuota."
    
    # Invia il messaggio al gruppo o alla chat privata
    await send_and_delete_message(chat_id, event, leaderboard_message, delay_leaderboard)




# Funzione per mandare un messaggio e cancellarlo dopo "delay" secondi
async def send_and_delete_message(chat_id, event, text, delay=4):

    # invio del messaggio    
    message = await event.reply(text)

    # attesa del delay specificato
    await asyncio.sleep(delay)
    # cancellamento del messaggio
    await client.delete_messages(chat_id, message)


# event listener 
@client.on(events.NewMessage())
async def handle_message(event):
    chat_id = event.chat_id

    # Controllo che il comando sia del reset dei punti
    if event.text == '/reset':
        # Controllo che l'ID sia dell'admin
        if event.sender_id == AdminUserID:
            reset_points(chat_id)
            await send_and_delete_message(chat_id, event, "I punteggi sono stati resettati per questa chat")
        else:
            await send_and_delete_message(chat_id, event, "non hai i permessi da admin")


    ## controllo che il messaggio sia una richiesta della leaderboard
    #if event.text == '/leaderboard':
    #    leaderboard = get_leaderboard(chat_id)
    #    if leaderboard:
    #        leaderboard_message = "\n".join([f"{username}: {points} points" for username, points in leaderboard])
    #    else:
    #        leaderboard_message = "La leaderboard è vuota."

    #    #await event.reply(leaderboard_message)
    #    await send_and_delete_message(chat_id, event, leaderboard_message)
    #    return



    if event.message.is_reply and event.text == 'Bless':
        original_message = await event.message.get_reply_message()
        original_sender_id = original_message.sender_id
        original_sender = await client.get_entity(original_sender_id)
        original_username = original_sender.first_name or original_sender.username
        if event.sender_id == AdminUserID:
            # aggiunge 100000 punti
            update_points(original_sender_id, chat_id, original_username, 100000)
            await send_and_delete_message(chat_id, event, f"{original_username} è stato benedetto con 100000 punti amicizia!")
        else: 
            return


    if event.message.is_reply and event.text == 'Nuke':
        original_message = await event.message.get_reply_message()
        original_sender_id = original_message.sender_id
        original_sender = await client.get_entity(original_sender_id)
        original_username = original_sender.first_name or original_sender.username
        if event.sender_id == AdminUserID:
            # aggiunge 100000 punti
            update_points(original_sender_id, chat_id, original_username, -100000)
            await send_and_delete_message(chat_id, event, f"{original_username} è stato annientato con -100000 punti amicizia!")
        else: 
            return
            
    # controllo che il messaggio contenga uno sticker e che si tratti di una risposta
    if isinstance(event.message.media, MessageMediaDocument) and event.message.is_reply:
        sticker_id = event.message.document.id  #  ID dello sticker

        # prende il nome e l'ID di chi ha mandato il messaggio originale
        original_message = await event.message.get_reply_message()
        original_sender_id = original_message.sender_id
        original_sender = await client.get_entity(original_sender_id)
        original_username = original_sender.first_name or original_sender.username
        
        # Controllo che uno non si cambi i punti da solo
        if event.sender_id == original_sender_id and sticker_id == STICKER_ADD_100_ID:
            await send_and_delete_message(chat_id, event, "non è possibile darsi punti da soli")
            return 

        # Controllo che uno non si cerchi di levare punti da solo
        if event.sender_id == original_sender_id and sticker_id == STICKER_SUB_100_ID:
            await send_and_delete_message(chat_id, event, "non è possibile levarsi punti da soli")
            return

        # aggiunge o leva punti in base all'ID
        if sticker_id == STICKER_ADD_100_ID:
            # aggiunge 100 punti
            update_points(original_sender_id, chat_id, original_username, 100)
            await send_and_delete_message(chat_id, event, f"{original_username} ha ottenuto 100 punti amicizia grandeee!")
        elif sticker_id == STICKER_SUB_100_ID:
            # leva 100 punti
            update_points(original_sender_id, chat_id, original_username, -100)
            await send_and_delete_message(chat_id, event, f"{original_username} ha perso 100 punti amicizia buuuu!")


try:
    client.start(bot_token=bot_token)
    print("Bot started and running...")
    client.run_until_disconnected()
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    conn.close()
    client.disconnect()
    print("Bot stopped.")