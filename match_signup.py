import discord
from discord.ext import commands
from datetime import datetime
from zoneinfo import ZoneInfo


DEV_CHANNEL_ID = 1366432462284128276

class MatchSignup(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    class SignupView(discord.ui.View):

        def __init__(self, title, match_text, timestamp_text=None):
            super().__init__()
            self.accepted = []
            self.declined = []
            self.tentatived = []
            self.match_title = title
            self.match_text = match_text
            self.timestamp_text = timestamp_text

        def remove_from_all(self, username):
            if username in self.accepted:
                self.accepted.remove(username)
            if username in self.declined:
                self.declined.remove(username)
            if username in self.tentatived:
                self.tentatived.remove(username)

        @discord.ui.button(label="✅ Accept", style=discord.ButtonStyle.success)
        async def accept(self, interaction: discord.Interaction,
                         button: discord.ui.Button):
            user = interaction.user.name
            self.remove_from_all(user)  # Erst überall raus
            self.accepted.append(user)  # Dann hinzufügen
            await interaction.response.edit_message(embed=self.build_embed())

        @discord.ui.button(label="❌ Decline", style=discord.ButtonStyle.danger)
        async def decline(self, interaction: discord.Interaction,
                          button: discord.ui.Button):
            user = interaction.user.name
            self.remove_from_all(user)
            self.declined.append(user)
            await interaction.response.edit_message(embed=self.build_embed())

        @discord.ui.button(label="❓ Tentative",
                           style=discord.ButtonStyle.primary)
        async def tentative(self, interaction: discord.Interaction,
                            button: discord.ui.Button):
            user = interaction.user.name
            self.remove_from_all(user)
            self.tentatived.append(user)
            await interaction.response.edit_message(embed=self.build_embed())

        def build_embed(self):
            description_text = self.match_text
            if self.timestamp_text:
                # Zeit + Matchbeschreibung + 2 Leerzeilen + ZeroWidthSpace
                description_text = f"{self.match_text}\n\n🕒 {self.timestamp_text}\n\u200b"

            embed = discord.Embed(title=self.match_title,
                                  description=description_text,
                                  color=discord.Color.blue())

            embed.add_field(name="✅ Accepted",
                            value="\n".join(self.accepted) or "None",
                            inline=True)
            embed.add_field(name="❌ Declined",
                            value="\n".join(self.declined) or "None",
                            inline=True)
            embed.add_field(name="❓ Tentative",
                            value="\n".join(self.tentatived) or "None",
                            inline=True)
            return embed

    @commands.command()
    async def creatematch(self,
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

            view = self.SignupView(title, smart_text, timestamp_text)
            embed = view.build_embed()
            await ctx.send(embed=embed, view=view)

            if ctx.channel.id != DEV_CHANNEL_ID:
                await ctx.message.delete() # <<< Diese Zeile löscht den !creatematch Befehl danach ✅ (nur wenn außerhalb des dev-channels)

        except ValueError:
            await ctx.send(
                "⚠️ Bitte gib das Datum und die Uhrzeit im Format `DD.MM.YYYY HH:MM` an!"
            )


async def setup(bot):
    await bot.add_cog(MatchSignup(bot))
