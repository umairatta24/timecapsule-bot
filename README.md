# timecapsule-bot

Most Discord bots react to what's happening right now. This one connects the present to the future.

Seal a message in a time capsule and it gets locked away — no edits, no take-backs. When the time comes, the bot reveals it publicly in your server and pings you. Your whole server watches it happen.

## Commands

| Command | Description |
|---|---|
| `/timecapsule` | Seal a message to be revealed at a future time |
| `/list` | See all your pending capsules |
| `/peek` | Check how long until your next capsule reveals |
| `/cancel` | Cancel a pending capsule before it reveals |
| `/leaderboard` | See who has sealed the most capsules in the server |

**Time formats:** `30s` · `6h` · `7d` · `2w` · `1m`

## Example
```
/timecapsule when:30d message:I think I'll have a job offer by then.
```

Thirty days later, the bot pings you in the channel:
```
⏳ Time Capsule Revealed!
@Flaming sealed this message on Tuesday, March 10, 2026:

I think I'll have a job offer by then.
```

## Setup

**Requirements:** Python 3.8+, a Discord bot token
```bash
git clone https://github.com/umairatta24/timecapsule-bot.git
cd timecapsule-bot
python3 -m venv venv
source venv/bin/activate
pip install discord.py python-dotenv
```

Create a `.env` file:
```
DISCORD_TOKEN=your-token-here
```

Run the bot:
```bash
python3 main.py
```

## How it works

1. Users seal messages with a time delay using `/timecapsule`
2. Each capsule is stored in a SQLite database with the user ID, channel ID, message, and reveal timestamp
3. A background task checks every 60 seconds for capsules that are due
4. When a capsule is due, the bot posts the reveal publicly in the original channel and pings the user
5. Capsules survive bot restarts because they're persisted to disk

## Project structure
```
main.py        # Bot setup, slash commands, background scheduler
database.py    # SQLite operations — create, read, reveal, delete
```

## Possible extensions

- `/setchannel` admin command to route all reveals to a designated channel
- Recurring capsules that reseal automatically after revealing
- Anonymous capsules that hide the author until reveal
- Web dashboard to manage capsules outside of Discord
