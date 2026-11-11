import sqlite3
from telethon import TelegramClient, sync, events    # events serve
from telethon.tl.functions.messages import GetStickerSetRequest
from telethon.tl.types import InputStickerSetShortName, MessageMediaDocument, DocumentAttributeSticker   # questi dovrebbero servire
import os
import asyncio
from dotenv import load_dotenv

# Load variables from .env file (to configure)
load_dotenv()  

# access variables
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")

client = TelegramClient('session_fp', api_id, api_hash)

# var for all the stickers id
STICKER_ADD_100_ID = int(os.getenv('STICKER_ADD_100_ID'))    # Sticker ID to add 100 p
STICKER_SUB_100_ID = int(os.getenv('STICKER_SUB_100_ID'))    # Sticker ID to subtract 100 p
STICKER_ADD_500_ID = int(os.getenv('STICKER_ADD_500_ID'))    # Sticker ID to add 500 p
STICKER_SUB_500_ID = int(os.getenv('STICKER_SUB_500_ID'))    # Sticker ID to subtract 500 p

AdminUserID = int(os.getenv('ADMIN_USER_ID'))

# setup DB SQLite 
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

#### DB FUNCTIONS

# change user points
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

# show leaderboard
def get_leaderboard(chat_id):
    cursor.execute("SELECT username, points FROM points WHERE chat_id = ? ORDER BY points DESC", (chat_id,))
    leaderboard = cursor.fetchall()
    return leaderboard

# reset points
def reset_points(chat_id):
    cursor.execute("DELETE FROM points WHERE chat_id = ?", (chat_id,))
    conn.commit()



#### Bot message communication functions

# func to send message and delete it after "delay" sec
async def send_and_delete_message(chat_id, event, text, delay=4):

    # send   
    message = await event.reply(text)

    # wait
    await asyncio.sleep(delay)
    # delete
    await client.delete_messages(chat_id, message)

# func to send message and delete the original and the new message after "delay" sec
async def send_and_delete_message_and_original(chat_id, event, text, delay=4):

    await event.message.delete()  
    message = await event.reply(text)

    await asyncio.sleep(delay)
    await client.delete_messages(chat_id, message)



#### Functions for simple commands

# Func for /help cmd
@client.on(events.NewMessage(pattern='/help'))
async def show_help(event):
    chat_id = event.chat_id
    delay_help = 15

    help_message = """Hi! I'm FriendBot, your bot for managing friendship points. Here's what I can do:

\n1. Friendship Points via Stickers

    To add or remove points from someone, reply to one of their messages with a specific sticker.

    Using a positive sticker (add points) will award the user friendship points.

    Using a negative sticker (remove points) will deduct friendship points from the user.

    Each sticker has a unique ID, and each group can have its own set of stickers configured to add or remove points.

\n2. /leaderboard command

    The /leaderboard command displays the ranking of all users in the chat and their friendship points.

    Points are displayed next to each user's name in the leaderboard.

\n3. /reset command

    The /reset command resets the points of all users in the group. Only an administrator can perform this action.

\nThese are the main commands. If you need any help, feel free to ask!

\nSee you around!"""
    
    # send msg to the group or private chat
    await send_and_delete_message_and_original(chat_id, event, help_message, delay_help)

# func to manage /leaderboard
@client.on(events.NewMessage(pattern='/leaderboard'))
async def show_leaderboard(event):
    chat_id = event.chat_id
    delay_leaderboard = 5

    leaderboard = get_leaderboard(chat_id)
    if leaderboard:
        leaderboard_message = "\n".join([f"{username}: {points} points" for username, points in leaderboard])
    else:
        leaderboard_message = "La leaderboard è vuota."
    
    # send msg to the group or private chat
    await send_and_delete_message_and_original(chat_id, event, leaderboard_message, delay_leaderboard)


#### MANAGEMENT OF STICKER RESPONSES

# event listener 
@client.on(events.NewMessage())
async def handle_message(event):
    chat_id = event.chat_id

    # see if the command is "reset"
    if event.text == '/reset':
        # admin check
        if event.sender_id == AdminUserID:
            reset_points(chat_id)
            await send_and_delete_message(chat_id, event, "Points resetted for this chat")
        else:
            await send_and_delete_message(chat_id, event, "You don't have admin permissions")


    if event.message.is_reply and event.text == 'Bless':
        original_message = await event.message.get_reply_message()
        original_sender_id = original_message.sender_id
        original_sender = await client.get_entity(original_sender_id)
        original_username = original_sender.first_name or original_sender.username
        if event.sender_id == AdminUserID:
            # add 100000 points
            update_points(original_sender_id, chat_id, original_username, 100000)
            await send_and_delete_message(chat_id, event, f"{original_username} is blessed with 100000 friendship points!")
        else: 
            return

    if event.message.is_reply and event.text == 'Nuke':
        original_message = await event.message.get_reply_message()
        original_sender_id = original_message.sender_id
        original_sender = await client.get_entity(original_sender_id)
        original_username = original_sender.first_name or original_sender.username
        if event.sender_id == AdminUserID:
            # remove 100000 points
            update_points(original_sender_id, chat_id, original_username, -100000)
            await send_and_delete_message(chat_id, event, f"{original_username} is annihilated with 100000 friendship points!")
        else: 
            return
            
    # check if msg is a sticker and a reply
    if isinstance(event.message.media, MessageMediaDocument) and event.message.is_reply:
        sticker_id = event.message.document.id  #  ID dello sticker

        # take sender ID
        original_message = await event.message.get_reply_message()
        original_sender_id = original_message.sender_id
        original_sender = await client.get_entity(original_sender_id)
        original_username = original_sender.first_name or original_sender.username
        
        # check for self awarding
        if event.sender_id == original_sender_id and (sticker_id == STICKER_ADD_100_ID or sticker_id == STICKER_ADD_500_ID):
            await send_and_delete_message(chat_id, event, "You can't give points to yourself")
            return 

        # Check for self removing points
        if event.sender_id == original_sender_id and (sticker_id == STICKER_SUB_100_ID or sticker_id == STICKER_SUB_500_ID):
            await send_and_delete_message(chat_id, event, "You can't remove points from yourself")
            return

        # add or remove points based on ID
        if sticker_id == STICKER_ADD_100_ID:
            # add 100 punti
            update_points(original_sender_id, chat_id, original_username, 100)
            await send_and_delete_message(chat_id, event, f"{original_username} gained 100 friendship points!")

        elif sticker_id == STICKER_SUB_100_ID:
            # remove 100 punti
            update_points(original_sender_id, chat_id, original_username, -100)
            await send_and_delete_message(chat_id, event, f"{original_username} lose 100 friendship points!")

        elif sticker_id == STICKER_ADD_500_ID:
            # add 500 punti
            update_points(original_sender_id, chat_id, original_username, 500)
            await send_and_delete_message(chat_id, event, f"{original_username} gained 500 friendship points!")

        elif sticker_id == STICKER_SUB_500_ID:
            # remove 500 punti
            update_points(original_sender_id, chat_id, original_username, -500)
            await send_and_delete_message(chat_id, event, f"{original_username} lose 500 friendship points!")


#### BOT START AND SHUTDOWN

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