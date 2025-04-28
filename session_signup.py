import discord
import json
import os
from discord.ext import commands
from datetime import datetime
from zoneinfo import ZoneInfo
from signup_view import SignupView

DEV_CHANNEL_ID = 1366432462284128276
EVENTS_CHANNEL_ID = 1366482974270558320
SESSIONS_FILE = "sessions.json"

class SessionSignup(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def createsession(self,
                          ctx,
                          title: str,
                          date: str,
                          time: str,
                          *,
                          match_text="React to join!"):
        try:
            # Datum + Uhrzeit zusammenbauen!
            dt_string = f"{date} {time}"  # z.B. "28.04.2025 20:00"
            dt = datetime.strptime(dt_string, "%d.%m.%Y %H:%M")

            # Deutsche Zeitzone setzen
            dt = dt.replace(tzinfo=ZoneInfo("Europe/Berlin"))

            # Unix Timestamp generieren
            timestamp = int(dt.timestamp())
            timestamp_text = f"<t:{timestamp}:f> — <t:{timestamp}:R>"

            # Beschreibung formatieren
            smart_text = match_text.replace("|", "\n").strip()

            id_suffix = title.lower().replace(" ", "_").replace("-", "_")

            view = SignupView(title, smart_text, timestamp_text)
            embed = view.build_embed()
            await ctx.send(embed=embed, view=view)

            # Speichere das Event im Event Channel
            events_channel = ctx.guild.get_channel(EVENTS_CHANNEL_ID)
            if events_channel:
                await events_channel.send(
                    f"id_suffix: {id_suffix}\n"
                    f"title: {title}\n"
                    f"match_text: {smart_text}\n"
                    f"timestamp_text: {timestamp_text}"
    )



            if ctx.channel.id != DEV_CHANNEL_ID:
                await ctx.message.delete() # <<< Diese Zeile löscht den !creatematch Befehl danach ✅ (wenn außerhalb des dev-channels)

        except ValueError:
            await ctx.send(
                "⚠️ Bitte gib das Datum und die Uhrzeit im Format `DD.MM.YYYY HH:MM` an!"
            )


async def setup(bot):
    await bot.add_cog(SessionSignup(bot))





