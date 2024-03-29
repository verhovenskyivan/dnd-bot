import discord
from discord.ext import commands
from discord.ui import Button, View, Select
import random
from items import items_prices

# Укажите намерения, которые ваш бот будет использовать
intents = discord.Intents.all()

intents.members = True  # Добавляем намерение для доступа к информации о членах сервера

# Префикс для команд бота
bot = commands.Bot(command_prefix='!', intents=intents, help_command=commands.DefaultHelpCommand())

# Функция для генерации предметов у торговца
async def generate_items():
    num_items = random.randint(3, 10)  # Генерируем случайное количество предметов от 1 до 5
    items = random.sample(list(items_prices.keys()), num_items)  # Выбираем случайные предметы из списка доступных
    return items

# Функция для получения цены предмета
async def get_item_price(item):
    return items_prices.get(item, "Цена неизвестна")

# Команда для генерации предметов у торговца
@bot.command(description="Показывает список предметов, доступных для покупки у торговца.")
async def shop(ctx):
    items = await generate_items()
    if items:
        await ctx.send("Торговец предлагает следующие предметы на продажу:")
        for item in items:
            price = await get_item_price(item)
            await ctx.send(f"{item}: {price}")
    else:
        await ctx.send("У торговца сегодня нет товаров.")

##############################################################

current_round = 1

async def start_action(ctx_or_interaction):
    global current_round
    current_round = 1
    if isinstance(ctx_or_interaction, discord.Interaction):
        await ctx_or_interaction.response.send_message(f'Бой начался, раунд {current_round}')
    else:
        await ctx_or_interaction.send(f'Бой начался, раунд {current_round}')

async def next_action(ctx_or_interaction):
    global current_round
    current_round_copy = current_round  # Создаем локальную копию переменной current_round
    if isinstance(ctx_or_interaction, discord.Interaction):
        # Получаем текущее сообщение
        message = ctx_or_interaction.message
        # Удаляем предыдущее сообщение
        await message.edit(content=f'Конец раунда {current_round_copy}')
        current_round += 1
        # Отправляем новое сообщение
        await ctx_or_interaction.response.send_message(f'Начало раунда {current_round}')
    else:
        await ctx_or_interaction.send(f'Конец раунда {current_round_copy}')
        current_round += 1
        await ctx_or_interaction.send(f'Начало раунда {current_round}')

async def end_action(ctx_or_interaction):
    if isinstance(ctx_or_interaction, discord.Interaction):
        # Отправляем новое сообщение о завершении боя
        await ctx_or_interaction.response.send_message('Бой закончен')
    else:
        # Отправляем новое сообщение о завершении боя
        await ctx_or_interaction.send('Бой закончен')

@bot.command(description="Бросок кубика")
async def roll(ctx, dice: str = None):
    if dice is None:
        # Создаем экземпляр View для отображения кнопок
        view = discord.ui.View()

        # Создаем кнопку выбора количества бросков
        roll_quantity_select = discord.ui.Select(
            placeholder="Выберите количество бросков",
            options=[
                discord.SelectOption(label=str(i), value=str(i)) for i in range(1, 21)
            ],
            custom_id='roll_quantity_select'
        )
        view.add_item(roll_quantity_select)

        # Отправляем сообщение с кнопками
        await ctx.send("Выберите количество бросков:", view=view)
    else:
        try:
            rolls, limit = map(int, dice.split('d'))
        except Exception:
            await ctx.send('Неправильный формат! Используйте XdY, где X - количество бросков, Y - количество граней')
            return

        result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
        await ctx.send(result)

@bot.command()
async def clear(ctx, amount: int = 5):
    if ctx.author.guild_permissions.manage_messages:
        try:
            messages = []
            async for message in ctx.channel.history(limit=None, oldest_first=True):
                messages.append(message)
                if len(messages) == amount + 5:
                    break
            await ctx.channel.delete_messages(messages[:-5])
            await ctx.send(f'Успешно удалены все сообщения, кроме последних 5!', delete_after=5)
        except discord.Forbidden:
            await ctx.send("У меня нет прав на удаление сообщений.")
        except discord.HTTPException:
            await ctx.send("Не удалось удалить сообщения.")
    else:
        await ctx.send("У вас нет прав на выполнение этой команды.")

##############################################################

@bot.command(description='Начало боя')
async def start(ctx):
    await start_action(ctx)

@bot.command(description='Конец раунда')
async def Next(ctx):
    await next_action(ctx)
    
@bot.command(description="Конец боя")
async def end(ctx):
    await end_action(ctx)

#------------------------------------------------------------------------------------
class CustomButton(discord.ui.Button['CustomButton']):
    def __init__(self, label, *, custom_id=None):
        super().__init__(label=label, style=discord.ButtonStyle.primary, custom_id=custom_id)

    async def callback(self, interaction: discord.Interaction):
        if self.label == 'Start':
            await start_action(interaction)
        elif self.label == 'Next':
            await next_action(interaction)
        elif self.label == 'End':
            await end_action(interaction)
        elif self.label == 'Roll':
            await roll_action(interaction)

@bot.command(description="Отображает меню с кнопками")
async def menu(ctx):
    view = discord.ui.View()
    buttons = [
        CustomButton(label='Start'),
        CustomButton(label='Next'),
        CustomButton(label='End'),
        CustomButton(label='Roll')
    ]
    for button in buttons:
        view.add_item(button)
    await ctx.send("Выберите действие:", view=view)

@bot.event
async def on_button_click(interaction):
    if interaction.custom_id == 'start_button':
        await start_action(interaction)
    elif interaction.custom_id == 'next_button':
        await next_action(interaction)
    elif interaction.custom_id == 'end_button':
        await end_action(interaction)
    elif interaction.custom_id == 'roll_button':
        await roll_action(interaction)

# Запуск бота
bot.run('')
