import asyncio
import base64
import datetime
import discord
import numpy as np
import pandas as pd
import pickle
import pytz
import tweepy
import yaml
import sys

from textblob import TextBlob

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from discord.ext import commands, tasks

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents, activity = discord.Activity(type = discord.ActivityType.watching, name = "All Tweets"))
tweet_sentiment_cache = pd.DataFrame()

def get_discord_token():
    keys = ''
    
    with open("Resources/Config.yaml") as file:
        keys = yaml.safe_load(file)

    token = keys["discord_api"]["client"]
    return token

def auth_to_tweepy():
    keys = ''
    
    with open("Resources/Config.yaml") as file:
        keys = yaml.safe_load(file)

    client = tweepy.Client(bearer_token=keys["search_tweets_api"]["bearer_token"], wait_on_rate_limit=True)
    return client

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

def get_user_info(client, id):
    user = client.get_user(id=id, user_fields="created_at,verified,public_metrics,description,profile_image_url")

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

def get_tweets_by_keyword(client, keyword):    
    tweet_ids = []
    tweet_times = []
    tweet_strings = []
    polarity_scores = []
    subjectivity_scores = []
    option_statuses = []

    # Get maximum number of Tweets from the last seven days that match a search keyword
    for tweet in tweepy.Paginator(client.search_recent_tweets, query=keyword, expansions = "author_id",  tweet_fields=['context_annotations', 'created_at'], max_results=100).flatten(limit=450):
        
        # Exclude retweets, we only want original thoughts
        if ("RT @" not in tweet.text):

            tweet_ids.append(tweet.id)
            tweet_times.append(tweet.created_at)
            tweet_strings.append(tweet.text)

            #Sentiment Analysis -> Polarity = -/+[-1,1] & Subjectivitiy = fact/feeling[0,1]
            polarity_scores.append(TextBlob(tweet.text).sentiment.polarity)
            subjectivity_scores.append(TextBlob(tweet.text).sentiment.subjectivity)

            account_features = get_user_info(client, tweet.author_id)
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

@tasks.loop(minutes=15)
async def get_data_task():
    global tweet_sentiment_cache
    print(f"Starting Data Loop...{datetime.datetime.now()}")
    client = auth_to_tweepy()
    dataframe = get_tweets_by_keyword(client, "cryptocurrency")
    dataframes = [tweet_sentiment_cache, dataframe]
    tweet_sentiment_cache = pd.concat(dataframes, sort=False)

@tasks.loop(minutes=60)
async def return_embed():
    print(f"Starting Embed Loop...{datetime.datetime.now()}")
    if return_embed.current_loop != 0:
        guilds = bot.guilds
        for guild in guilds:
            channel_id = 0

            for channel in guild.channels:
                if channel.name=='general':
                    channel_id = channel.id 

            if channel_id != 0:
                message_channel = bot.get_channel(channel_id)

        embed = get_sentiment(tweet_sentiment_cache)
        tweet_sentiment_cache.iloc[0:0]
        await message_channel.send(embed=embed)

async def main():
    async with bot:
        get_data_task.start()
        return_embed.start()
        token = get_discord_token()
        await bot.start(token)

asyncio.run(main())