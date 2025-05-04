import discord
import os
from discord.ext import commands
from zoneinfo import ZoneInfo
from datetime import datetime
from dotenv import load_dotenv

load_dotenv() 

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
ARRIVALS_CHANNEL_ID = int(os.getenv('ARRIVALS_CHANNEL_ID'))
DEPARTURES_CHANNEL_ID = int(os.getenv('DEPARTURES_CHANNEL_ID'))
DEPLOYMENT_LOGGING_CHANNEL_ID = int(os.getenv('DEPLOYMENT_LOGGING_CHANNEL_ID'))

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    await bot.load_extension("session_signup")
    log_channel = bot.get_channel(DEPLOYMENT_LOGGING_CHANNEL_ID)
    if log_channel:
        timestamp = datetime.now().strftime("%d.%m.%Y %H:%M")
        try:
            from zoneinfo import ZoneInfo
            now = datetime.now(ZoneInfo("Europe/Berlin"))
        except Exception as e:
            print(f"⚠️ Zeitzonenfehler: {e}")
            now = datetime.now()

        timestamp = now.strftime("%d.%m.%Y %H:%M")

        await log_channel.send(f"🚀 DK Legacy Bot wurde neu deployed ({timestamp})")


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