import discord
import os
import json
from discord.ext import commands
from signup_view import SignupView
from zoneinfo import ZoneInfo

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
ARRIVALS_CHANNEL_ID = 1365770366819242045
DEPARTURES_CHANNEL_ID = 1366018627584655481
DEPLOYMENT_LOGGING_CHANNEL_ID = 1366461721098715186
EVENTS_CHANNEL_ID = 1366482974270558320

SESSIONS_FILE = "sessions.json"

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    await bot.load_extension("session_signup")
    log_channel = bot.get_channel(DEPLOYMENT_LOGGING_CHANNEL_ID)
    if log_channel:
        from datetime import datetime
        now = datetime.now(ZoneInfo("Europe/Berlin"))
        timestamp = now.strftime("%d.%m.%Y %H:%M")
        await log_channel.send(f"🚀 DK Legacy Bot wurde neu deployed ({timestamp})")
    
    # Sessions laden und Views wieder registrieren
    event_channel = bot.get_channel(EVENTS_CHANNEL_ID)
    if event_channel:
        async for message in event_channel.history(limit=100):  # Oder mehr, wenn nötig
            id_suffix = message.content.strip()
            print(f'EVENT: {id_suffix}')
            # Hier musst du dann deine SessionViews neu registrieren
            view = SignupView.load_from_id_suffix(id_suffix)
            print(f'view {view}')
            bot.add_view(view)


async def load_sessions():
    if not os.path.exists(SESSIONS_FILE):
        return []
    try:
        with open(SESSIONS_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


@bot.event
async def on_member_join(member):
    guild = member.guild
    channel = guild.get_channel(ARRIVALS_CHANNEL_ID)
    if channel:
        await channel.send(
            f"✈️ Welcome aboard, {member.mention}! Get ready to leave your mark at DK Legacy! ⚡"
        )

@bot.event
async def on_member_remove(member):
    guild = member.guild
    channel = guild.get_channel(DEPARTURES_CHANNEL_ID)
    if channel:
        await channel.send(f"👋 {member.name} has left DK Legacy.")

        from discord.ext import commands

# Achtung: Nur User mit "Nachrichten verwalten"-Rechten dürfen den Befehl benutzen
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clearall(ctx):
    await ctx.channel.purge()



bot.run(DISCORD_TOKEN)
