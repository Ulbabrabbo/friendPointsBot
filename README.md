# FriendBot

FriendBot is a Telegram bot designed to manage friendship points in Telegram groups using custom stickers.

Users can award or deduct points from other members by replying to their messages with specific stickers.

## Features

- **+100 points:** Reply to a message with the configured +100 sticker.
- **-100 points:** Reply to a message with the configured -100 sticker.
- **+500 points:** Reply to a message with the configured +500 sticker.
- **-500 points:** Reply to a message with the configured -500 sticker.
- **Leaderboard:** Display the ranking of users in the group using `/leaderboard`.
- **Reset:** Reset all friendship points in the current group using `/reset` (admin only).
- **Help:** Display the bot instructions using `/help`.
- **Admin commands:**
  - `Bless`: Award 100,000 points to the replied user.
  - `Nuke`: Deduct 100,000 points from the replied user.

Users cannot award or deduct points from themselves using stickers.

Points are stored in a local SQLite database and are tracked separately for each Telegram group.

## Requirements

- Python 3.9 or newer.
- A Telegram account.
- A Telegram bot created through [@BotFather](https://t.me/BotFather).
- Telegram API credentials.
- Git (optional).

## Installation

Clone the repository:

```bash
git clone YOUR_REPOSITORY_URL
cd friendPointsBot
```

Install the required dependencies:

```bash
pip install telethon python-dotenv
```

Alternatively, you can use a virtual environment:

**Windows:**

```powershell
python -m venv venv
venv\Scripts\activate
```

**Linux / macOS:**

```bash
python3 -m venv venv
source venv/bin/activate
```

Then install the dependencies:

```bash
pip install telethon python-dotenv
```

## Environment Configuration (.env)

An example environment configuration file is provided in the repository (e.g. `.env.example`).

Create a copy of it and rename the copy to `.env`.

The `.env` file must be located in the same directory as the main Python script.

Populate it with the following values:

```dotenv
API_ID=
API_HASH=
BOT_TOKEN=

STICKER_ADD_100_ID=
STICKER_SUB_100_ID=
STICKER_ADD_500_ID=
STICKER_SUB_500_ID=

ADMIN_USER_ID=
```

### 1. API_ID and API_HASH

These credentials allow Telethon to connect to Telegram.

1. Visit [https://my.telegram.org](https://my.telegram.org).
2. Log in using your Telegram phone number.
3. Open **API development tools**.
4. Create an application if you don't already have one.
5. Copy your `API_ID` and `API_HASH` into the `.env` file.

### 2. BOT_TOKEN

The bot token is required to authenticate FriendBot.

1. Open Telegram and search for [@BotFather](https://t.me/BotFather).
2. Start a conversation using `/start`.
3. Use `/newbot` to create a new bot, or `/mybots` to manage an existing one.
4. Select your bot and retrieve its API token.
5. Copy the token into `BOT_TOKEN`.

**Keep your token private. Never commit your `.env` file to GitHub.**

### 3. Sticker IDs

Each sticker used by FriendBot must be identified by its Telegram document ID.

The repository includes a helper script called `stickerIDBot.py` to retrieve these IDs.

To use it:

1. Make sure your `.env` contains valid `API_ID`, `API_HASH` and `BOT_TOKEN` values.
2. Run the script:

```bash
python stickerIDBot.py
```

3. Send the desired stickers to the bot.
4. The script will print their corresponding sticker IDs in the terminal.
5. Copy each ID into the appropriate variable in `.env`.

Configure the four sticker IDs as follows:

| Environment variable | Purpose |
|---|---|
| `STICKER_ADD_100_ID` | Sticker that awards 100 points |
| `STICKER_SUB_100_ID` | Sticker that deducts 100 points |
| `STICKER_ADD_500_ID` | Sticker that awards 500 points |
| `STICKER_SUB_500_ID` | Sticker that deducts 500 points |

Make sure each sticker ID corresponds to the correct sticker.

### 4. ADMIN_USER_ID

This is the numeric Telegram user ID of the administrator authorized to use privileged commands such as `/reset`, `Bless` and `Nuke`.

You can retrieve it using the helper script `get_my_id.py`.

Run:

```bash
python get_my_id.py
```

The script will connect to Telegram using your personal Telegram account and print your numeric user ID.

If prompted, enter your phone number and the verification code sent by Telegram.

Copy the resulting ID into:

```dotenv
ADMIN_USER_ID=123456789
```

Note: This must be your personal Telegram user ID, not the bot's ID.

## Running FriendBot

Once the `.env` file is correctly configured, start the bot:

```bash
python friendPoints.py
```

If everything is configured correctly, you should see:

```text
Bot started and running...
```

FriendBot will now listen for messages in all Telegram groups where it has been added and has the necessary permissions.

The script must remain running for the bot to work.

## Database

FriendBot uses SQLite to store friendship points.

The database file is automatically created as:

```text
friend_points.db
```

Points are stored separately for each group, meaning that the same user can have different scores in different groups.

You can inspect or manually edit the database using tools such as [DB Browser for SQLite](https://sqlitebrowser.org/).

**Important:** Stop FriendBot before manually modifying the database to avoid SQLite write conflicts.

## Telegram Permissions

Make sure FriendBot:

- Has been added to the desired groups.
- Can receive messages and stickers.
- Has permission to send messages.
- Has permission to delete its own messages.

If the bot cannot receive regular group messages, check its privacy settings through BotFather using `/setprivacy`.


Keep your API credentials, bot token, Telegram sessions and database private.
