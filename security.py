import disnake
from disnake.ext import commands
from disnake.ui import Button, View, Modal, TextInput
import logging

# Настраиваем логирование для отслеживания работы бота
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Создаем объект Intents и включаем необходимые интенты
intents = disnake.Intents.default()
intents.members = True  # Для работы с участниками
intents.message_content = True  # Для доступа к содержимому сообщений

# Инициализируем бота с указанными интентами
bot = commands.Bot(command_prefix="!", intents=intents)

# Указываем ID канала, в который будут отправляться лог-сообщения
LOG_CHANNEL_ID = 1276183097351868511  # Замените на ID вашего канала для логов

# Список ID ролей, для которых бот будет игнорировать права и не банить
IGNORE_ROLE_IDS = {
    1246500782661046404, 1254920793750634618, 1250922098486935603,
    1250922054535086140, 1246500933287022695, 1277741958877417580, 1276222225674141728
}  # Замените на свои ID ролей

@bot.event
async def on_member_join(member):
    # Проверяем, если новый участник - это бот
    if member.bot:
        inviter = await find_inviter(member)
        if inviter:
            try:
                guild = member.guild
                bot_member = guild.me  # Получаем объект бота на сервере
                # Проверяем, можно ли банить инвайтера
                if inviter.top_role.position < bot_member.top_role.position:
                    await inviter.ban(reason="🚫 Попытка добавить бота на сервер")
                    logger.info(f"Инвайтер {inviter.name} забанен.")
                    
                    log_channel = bot.get_channel(LOG_CHANNEL_ID)
                    if log_channel:
                        await log_channel.send(
                            embed=disnake.Embed(
                                title="🔨 Инвайтер забанен",
                                description=(
                                    f"**Инвайтер:** {inviter.name} (ID: {inviter.id})\n"
                                    f"**Причина:** Попытка добавить бота на сервер\n"
                                    f"**Сервер:** {member.guild.name}\n"
                                    f"**Бан выполнен ботом:** {bot.user.name}"
                                ),
                                color=disnake.Color.red()
                            ).set_footer(text="Krexx Security")
                        )
                    
                    # Отправляем личное сообщение инвайтеру
                    view = ReportErrorView()
                    try:
                        await inviter.send(
                            embed=disnake.Embed(
                                title="❌ Вы были забанены",
                                description=(
                                    f"Вы были забанены анти-краш системой сервера **{member.guild.name}** "
                                    f"за попытку добавить бота: **{member.name}**.\n\n"
                                    "Если вы считаете, что бан был ошибочным, обратитесь к администрации сервера.\n\n"
                                    "**Инструкция:**\n"
                                    "1. Перейдите на этот сервер: https://discord.gg/HYxFTGU9\n"
                                    "2. Предоставьте подробности о произошедшем.\n"
                                    "3. Ожидайте рассмотрения вашей заявки.\n\n"
                                    "*.*"
                                ),
                                color=disnake.Color.blue()
                            ).set_footer(text="ShadowMoon Security"),
                            view=view
                        )
                    except disnake.Forbidden:
                        logger.warning(f"Не удалось отправить личное сообщение пользователю {inviter.name}. Личные сообщения отключены.")
                    except disnake.HTTPException as e:
                        logger.error(f"Ошибка при попытке отправить личное сообщение пользователю {inviter.name}: {e}")
                else:
                    logger.warning(f"Не удалось забанить инвайтера {inviter.name}, так как его роль выше роли бота.")
            except disnake.Forbidden as e:
                logger.error(f"Ошибка при попытке забанить инвайтера {inviter.name}: {e}")

        try:
            guild = member.guild
            bot_member = guild.me  # Получаем объект бота на сервере
            # Проверяем, можно ли забанить бота
            if member.top_role.position < bot_member.top_role.position:
                await member.ban(reason="🚫 Автоматический бан бота анти-краш системой")
                logger.info(f"Бот {member.name} забанен.")

                log_channel = bot.get_channel(LOG_CHANNEL_ID)
                if log_channel:
                    await log_channel.send(
                        embed=disnake.Embed(
                            title="🔨 Бан бота",
                            description=(
                                f"**Бот:** {member.name} (ID: {member.id})\n"
                                f"**Причина:** Автоматический бан анти-краш системы\n"
                                f"**Сервер:** {member.guild.name}\n"
                                f"**Бан выполнен ботом:** {bot.user.name}"
                            ),
                            color=disnake.Color.red()
                        ).set_footer(text="Krexx Security")
                    )

                # Отправляем личное сообщение забаненному боту
                view = ReportErrorView()
                try:
                    await member.send(
                        embed=disnake.Embed(
                            title="❌ Вы были забанены",
                            description=(
                                f"Вы были забанены анти-краш системой сервера **{member.guild.name}**.\n\n"
                                "**Инструкция:**\n"
                                "1. Перейдите на этот сервер: https://discord.gg/HYxFTGU9\n"
                                "2. Предоставьте подробности о произошедшем.\n"
                                "3. Ожидайте рассмотрения вашей заявки.\n\n"
                            ),
                            color=disnake.Color.blue()
                        ).set_footer(text="Krexx Security"),
                        view=view
                    )
                except disnake.Forbidden:
                    logger.warning(f"Не удалось отправить личное сообщение пользователю {member.name}. Личные сообщения отключены.")
                except disnake.HTTPException as e:
                    logger.error(f"Ошибка при попытке отправить личное сообщение пользователю {member.name}: {e}")
            else:
                logger.warning(f"Не удалось забанить бота {member.name}, так как его роль выше роли бота.")
        except disnake.Forbidden as e:
            logger.error(f"Ошибка при попытке забанить бота {member.name}: {e}")

@bot.event
async def on_member_update(before, after):
    # Проверяем, добавились ли новые роли и действуем, если это бот
    if len(before.roles) < len(after.roles):
        new_roles = [role for role in after.roles if role not in before.roles]
        
        for role in new_roles:
            if role.id in IGNORE_ROLE_IDS:
                # Если добавленная роль в списке игнорируемых, не предпринимаем действий
                logger.info(f"Участник {after.name} добавил роль {role.name}, но это не бот. Никаких действий не предпринято.")
                return

async def find_inviter(member):
    try:
        # Ищем, кто добавил бота на сервер
        logs = await member.guild.audit_logs(action=disnake.AuditLogAction.bot_add, limit=1).flatten()
        if logs:
            inviter = logs[0].user
            logger.info(f"Инвайтер найден: {inviter.name} (ID: {inviter.id})")
            return inviter
        else:
            logger.info("Инвайтер не найден.")
            return None
    except Exception as e:
        logger.error(f"Ошибка при поиске инвайтера: {e}")
        return None

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')

    # Устанавливаем статус бота
    game = disnake.Game(name="/info")
    await bot.change_presence(activity=game)

class ReportErrorView(View):
    def __init__(self):
        super().__init__(timeout=180.0)
        self.add_item(ReportErrorButton())

@bot.slash_command(name="info", description="Получите информацию о функциях бота")
async def info(ctx: disnake.ApplicationCommandInteraction):
    embed = disnake.Embed(
        title="Приветствуем вас!",
        description=(
            "Этот бот предназначен для защиты вашего сервера от различных угроз, связанных с ботами и их действиями. "
            "Он предлагает надежную защиту и контроль, чтобы ваш сервер оставался безопасным и стабильным."
        ),
        color=0x00ff00  # Вы можете выбрать любой цвет
    )
    
    embed.add_field(
        name="**Вот основные функции нашего бота:**",
        value=(
            "1. **Борьба с несанкционированными ботами:** Бот автоматически обнаруживает и банит ботов, "
            "которые добавляются на сервер без разрешения.\n"
            "2. **Предотвращение атак на сервер:** Обнаруживает и предотвращает атаки, связанные с массовым "
            "добавлением ботов, чтобы обеспечить стабильность вашего сервера.\n"
            "3. **Мониторинг подозрительных действий:** Уведомляет администраторов о подозрительных действиях, "
            "таких как массовое добавление ботов или изменение ролей."
        ),
        inline=False
    )
    
    embed.add_field(
        name="**Приоритеты нашего бота:**",
        value=(
            "1. Защита от несанкционированных ботов и попыток краша сервера.\n"
            "2. Уведомление администраторов о подозрительных действиях и потенциальных угрозах.\n"
            "3. Обеспечение общей безопасности и стабильности вашего сервера."
        ),
        inline=False
    )
    
    embed.add_field(
        name="**Разработан командой:**",
        value=(
            "Krexx Security. Мы стремимся предоставить наилучший опыт и защиту для вашего сервера. В ближайшем "
            "будущем бот станет доступен для использования на всех серверах. Оставайтесь с нами, чтобы быть в "
            "курсе последних обновлений и новостей!"
        ),
        inline=False
    )
    
    await ctx.send(embed=embed)

class ReportErrorButton(Button):
    def __init__(self):
        super().__init__(label="Мы заботимся о безопасности!", style=disnake.ButtonStyle.red, custom_id="report_error")

    async def callback(self, interaction: disnake.Interaction):
        modal = ErrorReportModal()
        await interaction.response.send_modal(modal)

class ErrorReportModal(Modal):
    def __init__(self):
        # Создаем модальное окно с текстовым полем для описания ошибки
        super().__init__(title="Мы заботимся о безопасности!", components=[])
        self.add_item(TextInput(label="Описание ошибки", placeholder="Опишите ошибку...", style=disnake.TextInputStyle.long))
    
    async def callback(self, interaction: disnake.Interaction):
        error_description = self.children[0].value
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(
                embed=disnake.Embed(
                    title="Мы заботимся о безопасности!",
                    description=(
                        f"**Сообщение от пользователя:** {interaction.user.name} (ID: {interaction.user.id})\n"
                        f"**Ошибка:** {error_description}"
                    ),
                    color=disnake.Color.red()
                ).set_footer(text="Krexx Security")
            )
        await interaction.response.send_message("✅ Спасибо! Ваше сообщение об ошибке было отправлено.", ephemeral=True)

bot.run("")
