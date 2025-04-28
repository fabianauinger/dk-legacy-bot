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

        # Dynamische Buttons erstellen
        self.add_buttons()

    def add_buttons(self):
        self.add_item(discord.ui.Button(label="✅", style=discord.ButtonStyle.success, custom_id=f"signup_accept_{self.id_suffix}"))
        self.add_item(discord.ui.Button(label="❌", style=discord.ButtonStyle.danger, custom_id=f"signup_decline_{self.id_suffix}"))
        self.add_item(discord.ui.Button(label="❓", style=discord.ButtonStyle.primary, custom_id=f"signup_tentative_{self.id_suffix}"))

    async def interaction_check(self, interaction: discord.Interaction):
        custom_id = interaction.data["custom_id"]
        user = interaction.user.name

        if f"accept_{self.id_suffix}" in custom_id:
            if user not in self.accepted:
                self.remove_from_all(user)
                self.accepted.append(user)
                await self.log_action(interaction, "✅")
        elif f"decline_{self.id_suffix}" in custom_id:
            if user not in self.declined:
                self.remove_from_all(user)
                self.declined.append(user)
                await self.log_action(interaction, "❌")
        elif f"tentative_{self.id_suffix}" in custom_id:
            if user not in self.tentatived:
                self.remove_from_all(user)
                self.tentatived.append(user)
                await self.log_action(interaction, "❓")

        await interaction.response.edit_message(embed=self.build_embed())
        return True

    def remove_from_all(self, username):
        if username in self.accepted:
            self.accepted.remove(username)
        if username in self.declined:
            self.declined.remove(username)
        if username in self.tentatived:
            self.tentatived.remove(username)

    def build_embed(self):
        description_text = self.match_text
        if self.timestamp_text:
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
                f"[{self.match_title}] - {interaction.user.name} hat auf {action} geklickt!"
            )

    @classmethod
    def load_from_id_suffix(cls, id_suffix):
        print(f'id_suffix  {id_suffix}')
        # Hier definierst du, wie eine Session beim Bot-Start aus einem ID-Suffix gebaut wird
        title = id_suffix.replace("_", " ").title()  # Z.B. "crylupus_cup" ➔ "Crylupus Cup"
        match_text = "React to join!"  # Standardtext
        timestamp_text = None  # Ohne genaue Uhrzeit beim Wiederherstellen

        return cls(title, id_suffix)
