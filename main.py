#create by diablo
import discord
from discord.ext import commands
import config

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)


class VerificationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Верифицироваться",
        style=discord.ButtonStyle.blurple,
        custom_id="verify_button"
    )
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        verified_role   = guild.get_role(config.VERIFIED_ROLE_ID)
        unverified_role = guild.get_role(config.UNVERIFIED_ROLE_ID)

        if not verified_role or not unverified_role:
            await interaction.response.send_message("❌ Одна из ролей не найдена!", ephemeral=True)
            return

        member = interaction.user
        if verified_role in member.roles:
            await interaction.response.send_message("✅ Ты уже верифицирован!", ephemeral=True)
            return

        await member.add_roles(verified_role, reason="Пользователь прошёл верификацию")
        await member.remove_roles(unverified_role, reason="Пользователь получил доступ")
        await interaction.response.send_message(" Верификация пройдена!", ephemeral=True)


@bot.event
async def setup_hook():
    bot.add_view(VerificationView())


@bot.event
async def on_ready():
    print(f"Бот {bot.user} запущен!")
    channel = bot.get_channel(config.TEXT_CHANNEL_ID)
    if channel is None:
        print(f"❌ Текстовый канал {config.TEXT_CHANNEL_ID} не найден!")
        return

    async for msg in channel.history(limit=50):
        if msg.author == bot.user and msg.components and any(
            comp.custom_id == "verify_button" for comp in msg.components[0].children
        ):
            print("ℹ️ Сообщение для верификации уже существует.")
            break
    else:
        embed = discord.Embed(
            title="Верификация",
            description="**Верифицируйся быстрее**",
            color=discord.Color.dark_gray()
        )
        embed.set_image(url=config.EMBED_BANNER_URL)

        await channel.send(embed=embed, view=VerificationView())
        print("✅ Сообщение для верификации отправлено.")


@bot.event
async def on_member_join(member: discord.Member):
    unverified_role = member.guild.get_role(config.UNVERIFIED_ROLE_ID)
    if unverified_role:
        try:
            await member.add_roles(unverified_role, reason="Новый участник получил роль unverified")
            print(f"✅ Назначена роль unverified для {member}")
        except Exception as e:
            print(f"❌ Не удалось назначить роль {member}: {e}")
    else:
        print("❌ Роль unverified не найдена!")


if __name__ == "__main__":
    bot.run(config.TOKEN)
