import discord
from discord import app_commands
from discord.ext import tasks
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta, timezone
from database import init_db, add_capsule, get_due_capsules, mark_revealed, get_user_capsules, delete_capsule

load_dotenv()

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

def parse_duration(duration_str):
    """Convert strings like 30s, 6h, 7d, 2w, 1m into a timedelta."""
    duration_str = duration_str.strip().lower()
    unit = duration_str[-1]
    try:
        value = int(duration_str[:-1])
    except ValueError:
        return None

    if unit == 's':
        return timedelta(seconds=value)
    elif unit == 'h':
        return timedelta(hours=value)
    elif unit == 'd':
        return timedelta(days=value)
    elif unit == 'w':
        return timedelta(weeks=value)
    elif unit == 'm':
        return timedelta(days=value * 30)
    else:
        return None

@client.event
async def on_ready():
    """Called when the bot connects to Discord."""
    guild = discord.Object(id=574069047751213076)
    tree.copy_global_to(guild=guild)
    await tree.sync(guild=guild)
    check_capsules.start()
    print(f"Time Capsule Bot is online as {client.user}")

@tree.command(name="timecapsule", description="Seal a message to be revealed in the future")
@app_commands.describe(
    when="How far in the future (e.g. 30s, 6h, 7d, 2w, 1m)",
    message="The message to seal in your time capsule"
)
async def timecapsule(interaction: discord.Interaction, when: str, message: str):
    delta = parse_duration(when)
    if delta is None:
        await interaction.response.send_message(
            "Invalid time format. Use `30s` for seconds, `6h` for hours, `7d` for days, `2w` for weeks, or `1m` for months.",
            ephemeral=True
        )
        return

    reveal_at = datetime.now(timezone.utc) + delta
    capsule_id = add_capsule(
        user_id=str(interaction.user.id),
        username=interaction.user.display_name,
        channel_id=str(interaction.channel.id),
        message=message,
        reveal_at=reveal_at
    )

    reveal_timestamp = int(reveal_at.timestamp())
    await interaction.response.send_message(
        f"🔒 Time capsule sealed! (ID: `{capsule_id}`)\n"
        f"Your message will be revealed <t:{reveal_timestamp}:R> on <t:{reveal_timestamp}:F>.",
        ephemeral=True
    )

@tree.command(name="list", description="See all your pending time capsules")
async def list_capsules(interaction: discord.Interaction):
    capsules = get_user_capsules(str(interaction.user.id))
    if not capsules:
        await interaction.response.send_message(
            "You have no pending time capsules.",
            ephemeral=True
        )
        return

    lines = ["**Your pending time capsules:**\n"]
    for row in capsules:
        capsule_id, message, created_at, reveal_at = row
        reveal_dt = datetime.fromisoformat(reveal_at)
        reveal_timestamp = int(reveal_dt.timestamp())
        preview = message[:50] + "..." if len(message) > 50 else message
        lines.append(f"**ID `{capsule_id}`** — reveals <t:{reveal_timestamp}:R>\n> {preview}")

    await interaction.response.send_message("\n".join(lines), ephemeral=True)

@tree.command(name="cancel", description="Cancel a pending time capsule")
@app_commands.describe(capsule_id="The ID of the capsule to cancel")
async def cancel_capsule(interaction: discord.Interaction, capsule_id: int):
    success = delete_capsule(capsule_id, str(interaction.user.id))
    if success:
        await interaction.response.send_message(
            f"✅ Capsule `{capsule_id}` has been cancelled.",
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            f"❌ Couldn't find capsule `{capsule_id}`. It may not exist, already be revealed, or belong to someone else.",
            ephemeral=True
        )

@tasks.loop(minutes=1)
async def check_capsules():
    """Check every minute for capsules that are due to be revealed."""
    due = get_due_capsules()
    for row in due:
        capsule_id, user_id, username, channel_id, message, created_at, reveal_at = row
        channel = client.get_channel(int(channel_id))
        if channel is None:
            continue

        created_dt = datetime.fromisoformat(created_at).replace(tzinfo=timezone.utc)
        created_timestamp = int(created_dt.timestamp())

        await channel.send(
            f"⏳ **Time Capsule Revealed!**\n"
            f"<@{user_id}> sealed this message on <t:{created_timestamp}:F>:\n\n"
            f">>> {message}"
        )
        mark_revealed(capsule_id)

init_db()
client.run(os.getenv("DISCORD_TOKEN"))