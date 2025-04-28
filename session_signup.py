import discord
import json
import os
from discord.ext import commands
from datetime import datetime
from zoneinfo import ZoneInfo
from signup_view import SignupView



DEV_CHANNEL_ID = 1366432462284128276
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
            # Datum + Uhrzeit zusammenbauen
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

            view = self.SignupView(title, smart_text, timestamp_text)
            embed = view.build_embed()
            await ctx.send(embed=embed, view=view)
            save_match(title, id_suffix)

            if ctx.channel.id != DEV_CHANNEL_ID:
                await ctx.message.delete() # <<< Diese Zeile löscht den !creatematch Befehl danach ✅ (wenn außerhalb des dev-channels)

        except ValueError:
            await ctx.send(
                "⚠️ Bitte gib das Datum und die Uhrzeit im Format `DD.MM.YYYY HH:MM` an!"
            )

        def save_match(title, id_suffix):
            if os.path.exists(SESSIONS_FILE):
                with open(SESSIONS_FILE, "r") as f:
                    matches = json.load(f)
            else:
                matches = []

            matches.append({
                "title": title,
                "id_suffix": id_suffix
            })

            with open(SESSIONS_FILE, "w") as f:
                json.dump(matches, f, indent=4)


async def setup(bot):
    await bot.add_cog(SessionSignup(bot))





