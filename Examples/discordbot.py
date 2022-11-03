import aiohttp
import asyncio
import discord
import json
import os
import random
import yaml

from discord.ext import commands, tasks

class DiscordV2Bot(commands.Bot):
    # Note: When using commands.Bot instead of discord.Client, the bot will
    # maintain its own tree instead.
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args, 
            **kwargs,
            intents = discord.Intents.all(),
            command_prefix = '!'
        )

        self.session = aiohttp.ClientSession()
        self.mod_channel_id = 1034614887411892315
        self.role_message_id = 1034629547548741652  # ID of the message that can be reacted to to add/remove a role.
        self.emoji_to_role = {
            discord.PartialEmoji(name='🔴'): 1034630529527586916,  # ID of the role associated with unicode emoji '🔴'.
            discord.PartialEmoji(name='🟡'): 1034630611203268618,  # ID of the role associated with unicode emoji '🟡'.
            discord.PartialEmoji(name='🟢'): 1034630622079111230,  # ID of the role associated with unicode emoji '🟢'.
        }

    async def on_ready(self) -> None:
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    async def on_member_join(self, member):
        guild = member.guild
        if guild.system_channel is not None:
            to_send = f'Welcome {member.mention} to {guild.name}!'
            await guild.system_channel.send(to_send)

    async def on_message(self, message: discord.Message) -> None:
        # we do not want the bot to reply to itself
        if message.author.id == self.user.id:
            return

        if message.content.startswith('!hello'):
            await message.reply('Hello!', mention_author=True)

        if message.content.startswith('!deleteme'):
            await message.channel.send('Goodbye in 3 seconds...', delete_after=3.0)

        if message.content.startswith('!editme'):
            msg = await message.channel.send('10')
            await asyncio.sleep(3.0)
            await msg.edit(content='40')

        if message.content.startswith('!guess'):
            await message.channel.send('Guess a number between 1 and 10.')

            def is_correct(m):
                return m.author == message.author and m.content.isdigit()

            answer = random.randint(1, 10)

            try:
                guess = await self.wait_for('message', check=is_correct, timeout=5.0)
            except asyncio.TimeoutError:
                return await message.channel.send(f'Sorry, you took too long it was {answer}.')

            if int(guess.content) == answer:
                await message.channel.send('You are right!')
            else:
                await message.channel.send(f'Oops. It is actually {answer}.')

        await self.process_commands(message)        

    async def on_message_delete(self, message):
        msg = f'{message.author} has deleted the message: {message.content}'
        await message.channel.send(msg)        

    async def on_message_edit(self, before, after):
        msg = f'**{before.author}** edited their message:\n{before.content} -> {after.content}'
        await before.channel.send(msg)

    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """Gives a role based on a reaction emoji."""
        # Make sure that the message the user is reacting to is the one we care about.
        if payload.message_id != self.role_message_id:
            return

        guild = self.get_guild(payload.guild_id)
        if guild is None:
            # Check if we're still in the guild and it's cached.
            return

        try:
            role_id = self.emoji_to_role[payload.emoji]
        except KeyError:
            # If the emoji isn't the one we care about then exit as well.
            return

        role = guild.get_role(role_id)
        if role is None:
            # Make sure the role still exists and is valid.
            return

        try:
            # Finally, add the role.
            await payload.member.add_roles(role)
        except discord.HTTPException:
            modchannel = self.get_channel(self.mod_channel_id)
            await modchannel.send("You are ratelimited")
            pass

    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        """Removes a role based on a reaction emoji."""
        # Make sure that the message the user is reacting to is the one we care about.
        if payload.message_id != self.role_message_id:
            return

        guild = self.get_guild(payload.guild_id)
        if guild is None:
            # Check if we're still in the guild and it's cached.
            return

        try:
            role_id = self.emoji_to_role[payload.emoji]
        except KeyError:
            # If the emoji isn't the one we care about then exit as well.
            return

        role = guild.get_role(role_id)
        if role is None:
            # Make sure the role still exists and is valid.
            return

        # The payload for `on_raw_reaction_remove` does not provide `.member`
        # so we must get the member ourselves from the payload's `.user_id`.
        member = guild.get_member(payload.user_id)
        if member is None:
            # Make sure the member still exists and is valid.
            return

        try:
            # Finally, remove the role.
            await member.remove_roles(role)
        except discord.HTTPException:
            # If we want to do something in case of errors we'd do it here.
            pass

    async def setup_hook(self) -> None:
        print("Starting tasks")
        self.get_Gas_Task.start()
        print("Loading cogs")
        for filename in os.listdir('./Examples/cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')
        self.activity = discord.Activity(type = discord.ActivityType.watching, name = f'{await self.get_Gas_Prices()}')

    async def close(self) -> None:
        await super().close()
        await self.session.close()

    async def start(self) -> None:
        await super().start(await self.get_discord_token(), reconnect=True)

    async def get_discord_token(self):
        keys = ''
        
        with open("Resources/Config.yaml") as file:
            keys = yaml.safe_load(file)

        token = keys["discord_api"]["client"]
        return token

    async def get_Etherscan_Key(self):
        config = ''

        with open("Resources/Config.yaml") as file:
            config = yaml.safe_load(file)

        key = config["etherscan"]["API_Key"]
        return key

    async def get_Gas_Prices(self):
        async with self.session.get(f'https://api.etherscan.io/api?module=gastracker&action=gasoracle&apikey={await self.get_Etherscan_Key()}') as response:
            
            gas_prices_content = await response.content.read()
            gas_prices_object = json.loads(gas_prices_content.decode("utf-8"))

            safe_gas_price = gas_prices_object['result']['SafeGasPrice']
            propose_gas_price = gas_prices_object['result']['ProposeGasPrice']
            fast_gas_price = gas_prices_object['result']['FastGasPrice']

            slow = (f'🐢 {safe_gas_price}|')
            medium = (f'🚌 {propose_gas_price}|')
            fast = (f'🚀 {fast_gas_price} (gwei)')
            
            return f'{slow} {medium} {fast}'

    @tasks.loop(seconds=1)
    async def get_Gas_Task(self) -> None:
        print("Getting gas prices...")
        output = await self.get_Gas_Prices()
        if output != self.activity.name:
            print("Changing bot activity...")
            await self.change_presence(activity = discord.Activity(type = discord.ActivityType.watching, name = f'{output}'))

    @get_Gas_Task.before_loop
    async def before(self) -> None:
        await self.wait_until_ready()
        print("Initializing gas task...")    

async def main() -> None:
    bot = DiscordV2Bot()
    await bot.start()

asyncio.run(main())