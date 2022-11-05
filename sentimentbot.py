import aiohttp
import asyncio
import base64
import datetime
import discord
import numpy as np
import os
import pandas as pd
import pickle
import pytz
import random
import sys
import yaml

from textblob import TextBlob

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from discord.ext import commands, tasks
from tweepy.asynchronous import AsyncClient, AsyncPaginator

def import_public_key(filename):
    with open(filename, 'rb') as pem_in:
        pemlines = pem_in.read()
    public_key = serialization.load_pem_public_key(pemlines, default_backend())
    return public_key

def import_signature(filename):
    with open(filename, 'rb') as sig_in:
        sig_lines = sig_in.read()
    signature = base64.urlsafe_b64decode(sig_lines)
    return signature

def verify_model(bytes):
    try:
        public_key = import_public_key('Resources/pubkey.cer')
        signature = import_signature('Resources/signature.sig')

        public_key.verify(
            signature=signature,
            data=bytes,
            padding=padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            algorithm=hashes.SHA256()
        )
        is_signature_correct = True
    except InvalidSignature:
        is_signature_correct = False
    
    return(is_signature_correct)

def get_xbg_model():
    file = open('Resources/model.pickle', 'rb')
    bytes = file.read()
    is_verified = verify_model(bytes)

    if(not is_verified):
        sys.exit("model.pickle has been altered. Check access permissions now!")

    with open('Resources/model.pickle', 'rb') as read_file:
        xgb_model = pickle.load(read_file)
        return xgb_model

async def get_user_info(client, id):
    user = await client.get_user(id=id, user_fields="created_at,verified,public_metrics,description,profile_image_url")

    if user.data is not None:

        account_age_days = (datetime.datetime.utcnow().replace(tzinfo=pytz.UTC) - user.data['created_at']).days

        if account_age_days == 0:
            account_age_days = 1

        if user.data['verified'] == True:
            verified = 1
        else:
            verified = 0

        if user.data['profile_image_url'] == 'https://abs.twimg.com/sticky/default_profile_images/default_profile_normal.png':
            default_profile_image = 1
        else:
            default_profile_image = 0

        followers_count = user.data['public_metrics']['followers_count']
        following_count = user.data['public_metrics']['following_count']
        tweet_count = user.data['public_metrics']['tweet_count']
        listed_count = user.data['public_metrics']['listed_count'] # Number of public lists that this user is a member of.
        average_tweets_per_day = np.round(tweet_count / account_age_days, 3)

        hour_created = user.data['created_at'].hour
        network = np.round(np.log(1 + following_count)* np.log(1 + followers_count), 3)
        tweet_to_followers = np.round(np.log(1 + tweet_count) * np.log(1 + followers_count), 3)
        follower_acq_rate = np.round(np.log(1 + (followers_count / account_age_days)), 3)
        following_acq_rate = np.round(np.log(1 + (following_count / account_age_days)), 3)
        listed_acq_rate = np.round(np.log(1 + listed_count) * np.log(1 + tweet_count), 3)

        account_features = [verified, hour_created, default_profile_image, listed_count, followers_count, following_count, tweet_count, average_tweets_per_day, network, tweet_to_followers, follower_acq_rate, following_acq_rate, listed_acq_rate]
    else:
        account_features = 'This user is not found'

    return account_features

def get_bot_probability(user_features, xgb_model):
    if user_features == 'User not found':
        return 'User not found'
    else:
        user = np.matrix(user_features)
        bot_probability = np.round(xgb_model.predict_proba(user)[:, 1][0]*100, 2)
        return bot_probability

def get_result(probability):
    if probability < 20:
        return 'Not a bot'
    elif probability < 35:
        return 'Likely not a bot'
    elif probability < 50:
        return 'Probably not a bot'
    elif probability < 60:
        return 'Maybe a bot'
    elif probability < 80:
        return 'Likely a bot'
    else:
        return 'Bot'

async def get_tweets_by_keyword(client, keyword):    
    tweet_ids = []
    tweet_times = []
    tweet_strings = []
    polarity_scores = []
    subjectivity_scores = []
    option_statuses = []

    # Get maximum number of Tweets from the last seven days that match a search keyword
    async for tweet in AsyncPaginator(client.search_recent_tweets, query=keyword, expansions = "author_id",  tweet_fields=['context_annotations', 'created_at'], max_results=100).flatten(limit=450):
        
        # Exclude retweets, we only want original thoughts
        if ("RT @" not in tweet.text):

            tweet_ids.append(tweet.id)
            tweet_times.append(tweet.created_at)
            tweet_strings.append(tweet.text)

            #Sentiment Analysis -> Polarity = -/+[-1,1] & Subjectivitiy = fact/feeling[0,1]
            polarity_scores.append(TextBlob(tweet.text).sentiment.polarity)
            subjectivity_scores.append(TextBlob(tweet.text).sentiment.subjectivity)

            account_features = await get_user_info(client, tweet.author_id)
            xgb_model = get_xbg_model()
            probability_score = get_bot_probability(account_features, xgb_model)
            option_status = get_result (probability_score)

            option_statuses.append(option_status)

    # Creating dataframe with desired info
    dataframe = pd.DataFrame({'id':tweet_ids, 'time': tweet_times, 'tweet': tweet_strings, 'polarity': polarity_scores, 'subjectivity': subjectivity_scores, 'account_activity': option_statuses})
    return dataframe

def get_sentiment(dataframe):
    sentiment_score = dataframe['polarity'].mean()
    
    option_statuses = dataframe['account_activity'].value_counts(normalize=True)

    if sentiment_score > 0.75 or sentiment_score == 0.75:
        result = "Sentiment is positive"
    elif sentiment_score > 0.45 or sentiment_score == 0.45:
        result =  "Sentiment is neutral"
    else:
        result =  "Sentiment is negative"

    Not_a_bot = option_statuses['Not a bot'] * 100
    Likely_not_a_bot = option_statuses['Likely not a bot'] * 100
    Probably_not_a_bot = option_statuses['Probably not a bot'] * 100
    Maybe_a_bot = option_statuses['Maybe a bot'] * 100
    Likely_a_bot = option_statuses['Likely a bot'] * 100
    Bot = option_statuses['Bot'] * 100

    embed = discord.Embed(
            title = f"",
            description = f"",
            color = discord.Color.blue()
        )

    embed.set_author(name = "Twitter", icon_url = "https://about.twitter.com/content/dam/about-twitter/en/brand-toolkit/brand-download-img-1.jpg.twimg.1920.jpg")

    embed.add_field(name = "Result", value = result, inline = True) 
    embed.add_field(name = "Not a bot", value = str(round(Not_a_bot, 2)) + "%", inline = True)
    embed.add_field(name = "Likely not a bot", value = str(round(Likely_not_a_bot, 2)) + "%", inline = True)
    embed.add_field(name = "Probably not a bot", value = str(round(Probably_not_a_bot, 2)) + "%", inline = True)
    embed.add_field(name = "Maybe a bot", value = str(round(Maybe_a_bot, 2)) + "%", inline = True)
    embed.add_field(name = "Likely a bot", value = str(round(Likely_a_bot, 2)) + "%", inline = True)
    embed.add_field(name = "Bot", value = str(round(Bot, 2)) + "%", inline = True)    
    
    return embed

class DiscordV2Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args, 
            **kwargs,
            intents = discord.Intents.all(),
            command_prefix = '!',
            activity = discord.Activity(type = discord.ActivityType.watching, name = "All Tweets")
        )

        self.session = aiohttp.ClientSession()
        self.tweet_sentiment_cache = pd.DataFrame()

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
        self.get_data_task.start()
        print("Loading cogs")
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')

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

    async def auth_to_tweepy(self):
        keys = ''
        
        with open("Resources/Config.yaml") as file:
            keys = yaml.safe_load(file)

        client = AsyncClient(bearer_token=keys["search_tweets_api"]["bearer_token"], wait_on_rate_limit=True)
        return client

    @tasks.loop(seconds=1)
    async def get_gas_task(self) -> None:
        print("Getting gas prices...")
        output = await self.get_gas_prices()
        if output != self.activity.name:
            print("Changing bot activity...")
            await self.change_presence(activity = discord.Activity(type = discord.ActivityType.watching, name = f'{output}'))

    @tasks.loop(minutes=15, reconnect=True)
    async def get_data_task(self) -> None:
        print(f"Starting Data Loop...{datetime.datetime.now()}")
        tweepy_client = await self.auth_to_tweepy()
        dataframe = await get_tweets_by_keyword(tweepy_client, "cryptocurrency")
        dataframes = [self.tweet_sentiment_cache, dataframe]
        self.tweet_sentiment_cache = pd.concat(dataframes, sort=False)

        count = self.get_data_task.current_loop + 1
        if self.get_data_task.current_loop != 0 and count % 4 == 0:
            print(f"Starting Embed Loop...{datetime.datetime.now()}")
            guilds = self.guilds
            for guild in guilds:
                channel_id = 0

                for channel in guild.channels:
                    if channel.name=='general':
                        channel_id = channel.id 

                if channel_id != 0:
                    message_channel = self.get_channel(channel_id)

            embed = get_sentiment(self.tweet_sentiment_cache)
            self.tweet_sentiment_cache.iloc[0:0]
            await message_channel.send(embed=embed)

async def main() -> None:
    bot = DiscordV2Bot()
    await bot.start()

asyncio.run(main())