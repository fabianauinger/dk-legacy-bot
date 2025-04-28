import discord
import os
import json
import asyncio
from discord.ext import commands
from signup_view import SignupView
from zoneinfo import ZoneInfo
from datetime import datetime

DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
ARRIVALS_CHANNEL_ID = 1365770366819242045
DEPARTURES_CHANNEL_ID = 1366018627584655481
DEPLOYMENT_LOGGING_CHANNEL_ID = 1366461721098715186
EVENTS_CHANNEL_ID = 1366482974270558320

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    log_channel = bot.get_channel(DEPLOYMENT_LOGGING_CHANNEL_ID)
    if log_channel:
        now = datetime.now(ZoneInfo("Europe/Berlin"))
        timestamp = now.strftime("%d.%m.%Y %H:%M")
        await log_channel.send(f"🚀 DK Legacy Bot wurde neu deployed ({timestamp})")

    await bot.wait_until_ready()
    await load_sessions_from_channel(bot)

async def load_sessions_from_channel(bot):
    events_channel = bot.get_channel(EVENTS_CHANNEL_ID)
    if not events_channel:
        print("⚠️ Kein Events-Channel gefunden.")
        return

    async for message in events_channel.history(limit=50):
        if message.author.bot and message.content.startswith("id_suffix:"):
            try:
                lines = message.content.splitlines()
                id_suffix = lines[0].split(": ", 1)[1]
                title = lines[1].split(": ", 1)[1]
                match_text = lines[2].split(": ", 1)[1].replace("|", "\n")
                timestamp_text = lines[3].split(": ", 1)[1]

                view = SignupView(title, match_text, id_suffix, timestamp_text)
                bot.add_view(view)
                print(f"✅ Session {title} geladen und View registriert!")
            except Exception as e:
                print(f"⚠️ Fehler beim Laden einer Session: {e}")

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

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clearall(ctx):
    await ctx.channel.purge()

async def main():
    await bot.load_extension("session_signup")
    await bot.start(DISCORD_TOKEN)

asyncio.run(main())
