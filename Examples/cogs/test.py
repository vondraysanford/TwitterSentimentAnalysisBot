import discord
import json
from discord import app_commands
from discord.ext import commands, tasks
from enum import Enum
from typing import Literal

class Test(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.ctx_menu = app_commands.ContextMenu(
            name='Report to Moderators',
            callback=self.report_message,
        )
        self.bot.tree.add_command(self.ctx_menu)

        # an attribute we can access from our task
        self.counter = 0

    async def cog_unload(self) -> None:
        self.bot.tree.remove_command(self.ctx_menu.name, type=self.ctx_menu.type)

    # This context menu command only works on messages 
    # Needs to be manually added-> https://github.com/Rapptz/discord.py/issues/7823
    async def report_message(self, interaction: discord.Interaction, message: discord.Message) -> None:
        # We're sending this response message with ephemeral=True, so only the command executor can see it
        await interaction.response.send_message(
            f'Thanks for reporting this message by {message.author.mention} to our moderators.', ephemeral=True
        )

        # Handle report by sending it into a log channel
        log_channel = interaction.guild.get_channel(1025588177647456287)  # replace with your channel id

        embed = discord.Embed(title='Reported Message')
        if message.content:
            embed.description = message.content

        embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
        embed.timestamp = message.created_at

        url_view = discord.ui.View()
        url_view.add_item(discord.ui.Button(label='Go to Message', style=discord.ButtonStyle.url, url=message.jump_url))

        await log_channel.send(embed=embed, view=url_view)
        
    async def get_Transaction_Time(self):
        async with self.bot.session.get(f'https://api.etherscan.io/api?module=gastracker&action=gasoracle&apikey={await self.bot.get_Etherscan_Key()}') as response:
            
            gas_prices_content = await response.content.read()
            gas_prices_object = json.loads(gas_prices_content.decode("utf-8"))
            fast_gas_price = gas_prices_object['result']['FastGasPrice']

            async with self.bot.session.get(f'https://api.etherscan.io/api?module=gastracker&action=gasestimate&gasprice={fast_gas_price}&apikey={await self.bot.get_Etherscan_Key()}') as response:
                transaction_time_content = await response.content.read()
                transaction_time_object = json.loads(transaction_time_content.decode("utf-8"))
                seconds = int(transaction_time_object['result']) % (24 * 3600)
                hour = seconds // 3600
                seconds %= 3600
                minutes = seconds // 60
                seconds %= 60

                return "%d:%02d:%02d" % (hour, minutes, seconds)

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print('Test Cog Loaded')
        print('------')
        self.my_background_task.start()

    @app_commands.describe(
        first_value='The first value you want to add something to',
        second_value='The value you want to add to the first value',
        )
    @app_commands.command(name='add',description='Add two values together')
    async def add(self, interaction: discord.Interaction, first_value: int, second_value: int) -> None:
    #     """Adds two numbers together."""
        await interaction.response.send_message(f'{first_value} + {second_value} = {first_value + second_value}')

    # The rename decorator allows us to change the display of the parameter on Discord.
    # In this example, even though we use `text_to_send` in the code, the client will use `text` instead.
    # Note that other decorators will still refer to it as `text_to_send` in the code.
    @app_commands.rename(text_to_send='text')
    @app_commands.describe(text_to_send='Text to send in the current channel')
    @app_commands.command(name='send' ,description='Send a message from the bot')
    async def send(self, interaction: discord.Interaction, text_to_send: str) -> None:
        """Sends the text into the current channel."""
        await interaction.response.send_message(text_to_send)

    # The "ephemeral" parameter only lets the user see this message
    @app_commands.command(name="secret", description='Sends a message just to you')
    async def secret(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(f'Hello World', ephemeral=True)

    @app_commands.command(name='shop')
    @app_commands.describe(action='The action to do in the shop', item='The target item')
    async def shop(self, interaction: discord.Interaction, action: Literal['Buy', 'Sell'], item: str):
        """Interact with the shop"""
        await interaction.response.send_message(f'Action: {action}\nItem: {item}')

    # The second way to do choices is via an Enum from the standard library
    # On Discord, this will show up as four choices: apple, banana, cherry, and dragonfruit
    # In the code, you will receive the appropriate enum value.
    class Fruits(Enum):
        apple = 0
        banana = 1
        cherry = 2
        dragonfruit = 3

    @app_commands.command(name='fruit')
    @app_commands.describe(fruit='The fruit to choose')
    async def fruit(self, interaction: discord.Interaction, fruit: Fruits):
        """Choose a fruit!"""
        await interaction.response.send_message(repr(fruit))

    @app_commands.command(name="transactiontime")
    async def transctiontime(self, interaction: discord.Interaction):
        await interaction.response.defer()
        message = await self.get_Transaction_Time()
        await interaction.followup.send(f"The fastest tx will send in {message}")

    @tasks.loop(seconds=60)  # task runs every 60 seconds
    async def my_background_task(self):
        channel = self.bot.get_channel(1034614887411892315)  # channel ID goes here
        self.counter += 1
        await channel.send(f"Task iterations since start: {self.counter}")

    @my_background_task.before_loop
    async def before_my_task(self):
        await self.bot.wait_until_ready()
        print("Initializing test task...")

async def setup(bot):
    await bot.add_cog(Test(bot))