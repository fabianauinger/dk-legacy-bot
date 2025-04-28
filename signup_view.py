import discord

TICK_LOGGING_CHANNEL_ID = 1366458949657690123

class SignupView(discord.ui.View):

        def __init__(self, title, match_text, id_suffix, timestamp_text=None):
            super().__init__(timeout=None)
            self.accepted = []
            self.declined = []
            self.tentatived = []
            self.match_title = title
            self.match_text = match_text
            self.timestamp_text = timestamp_text
            self.id_suffix = id_suffix 

        def remove_from_all(self, username):
            if username in self.accepted:
                self.accepted.remove(username)
            if username in self.declined:
                self.declined.remove(username)
            if username in self.tentatived:
                self.tentatived.remove(username)

        @discord.ui.button(label="✅", style=discord.ButtonStyle.success, custom_id="signup_accept_{self.id_suffix}")
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


        @discord.ui.button(label="❌", style=discord.ButtonStyle.danger, custom_id="signup_decline_{self.id_suffix}")
        async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
            user = interaction.user.name
            if user in self.declined:
                await interaction.response.defer()
                return
            self.remove_from_all(user)
            self.declined.append(user)
            await self.log_action(interaction, button.label)
            await interaction.response.edit_message(embed=self.build_embed())

        @discord.ui.button(label="❓", style=discord.ButtonStyle.primary, custom_id="signup_tentative_{self.id_suffix}")
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
            description_text = self.match_text
            if self.timestamp_text:
                # Zeit + Matchbeschreibung + 2 Leerzeilen + ZeroWidthSpace
                description_text = f"{self.match_text}\n\n🕒 {self.timestamp_text}\n\u200b"

            embed = discord.Embed(title=self.match_title,
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
                    f"[{self.match_title}] - {interaction.user.name} hat auf {action} geklickt!."
                )