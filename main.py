import discord
import os
from discord.ext import commands
from keep_alive import keep_alive

keep_alive()  # Keep the bot alive

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
ARRIVALS_CHANNEL_ID = 1365770366819242045
DEPARTURES_CHANNEL_ID = 1366018627584655481


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    await bot.load_extension("match_signup")


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


bot.run(DISCORD_TOKEN)
