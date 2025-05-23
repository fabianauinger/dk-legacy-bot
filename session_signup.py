import discord
import os
from discord.ext import commands
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

load_dotenv() 


DEV_CHANNEL_ID = int(os.getenv('DEV_CHANNEL_ID'))
TICK_LOGGING_CHANNEL_ID = int(os.getenv('TICK_LOGGING_CHANNEL_ID'))

class SessionSignup(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    class SignupView(discord.ui.View):

        def __init__(self, session_title, session_text, timestamp_text=None):
            super().__init__(timeout=None)
            self.accepted = []
            self.declined = []
            self.tentatived = []
            self.session_title = session_title
            self.session_text = session_text
            self.timestamp_text = timestamp_text

        def remove_from_all(self, username):
            if username in self.accepted:
                self.accepted.remove(username)
            if username in self.declined:
                self.declined.remove(username)
            if username in self.tentatived:
                self.tentatived.remove(username)

        @discord.ui.button(label="✅", style=discord.ButtonStyle.success)
        async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
            user = interaction.user.name
            if user in self.accepted:
                # ✅ User ist schon Accepted -> NICHTS machen
                await interaction.response.defer()  # Antwort abschließen ohne Fehler
                return
            # ❌ User muss wechseln
            self.remove_from_all(user)
            self.accepted.append(user)
            await self.log_action(interaction, button.label)
            await interaction.response.edit_message(embed=self.build_embed())


        @discord.ui.button(label="❌", style=discord.ButtonStyle.danger)
        async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
            user = interaction.user.name
            if user in self.declined:
                await interaction.response.defer()
                return
            self.remove_from_all(user)
            self.declined.append(user)
            await self.log_action(interaction, button.label)
            await interaction.response.edit_message(embed=self.build_embed())

        @discord.ui.button(label="❓", style=discord.ButtonStyle.primary)
        async def tentative(self, interaction: discord.Interaction, button: discord.ui.Button):
            user = interaction.user.name
            if user in self.tentatived:
                await interaction.response.defer()
                return
            self.remove_from_all(user)
            self.tentatived.append(user)
            await self.log_action(interaction, button.label)
            await interaction.response.edit_message(embed=self.build_embed())


        def build_embed(self):
            description_text = self.session_text
            if self.timestamp_text:
                # Zeit + Sessionbeschreibung + 2 Leerzeilen + ZeroWidthSpace
                description_text = f"{self.session_text}\n\n🕒 {self.timestamp_text}\n\u200b"

            embed = discord.Embed(title=self.session_title,
                                  description=description_text,
                                  color=discord.Color.blue())

            embed.add_field(name="Accepted ✅",
                            value="\n".join(self.accepted) or "None",
                            inline=True)
            embed.add_field(name="Declined ❌",
                            value="\n".join(self.declined) or "None",
                            inline=True)
            embed.add_field(name="Tentative ❓",
                            value="\n".join(self.tentatived) or "None",
                            inline=True)
            return embed
        
        async def log_action(self, interaction: discord.Interaction, action: str):
            log_channel = interaction.guild.get_channel(TICK_LOGGING_CHANNEL_ID)
            if log_channel:
                await log_channel.send(
                    f"[{self.session_title}] - {interaction.user.name} hat auf {action} geklickt!."
                )

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def createsession(self,
                          ctx,
                          session_title: str,
                          date: str,
                          time: str,
                          *,
                          session_text="React to join!"):
        try:
            # Datum + Uhrzeit zusammenbauen
            dt_string = f"{date} {time}"  # z.B. "28.04.2025 20:00"
            dt = datetime.strptime(dt_string, "%d.%m.%Y %H:%M")
            print(f'Parsed datetime: {dt}')

            # Deutsche Zeitzone setzen
            dt = dt.replace(tzinfo=ZoneInfo("Europe/Berlin"))

            # Unix Timestamp generieren
            timestamp = int(dt.timestamp())
            timestamp_text = f"<t:{timestamp}:f> — <t:{timestamp}:R>"

            # Beschreibung formatieren
            smart_text = session_text.replace("|", "\n").strip()

            view = self.SignupView(session_title, smart_text, timestamp_text)
            embed = view.build_embed()
            await ctx.send(embed=embed, view=view)

            if ctx.channel.id != DEV_CHANNEL_ID:
                await ctx.message.delete() # <<< Diese Zeile löscht den !createsession Befehl danach ✅ (nur wenn außerhalb des dev-channels)

        except ValueError:
            await ctx.send(
                "⚠️ Bitte gib das Datum und die Uhrzeit im Format `DD.MM.YYYY HH:MM` an!"
            )


async def setup(bot):
    await bot.add_cog(SessionSignup(bot))