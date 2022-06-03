import csv
import datetime
import pandas as pd
import numpy as np
import pytz
import tweepy
import yaml

from dateutil import parser

# Load dataset
raw_df = pd.read_csv("twitter_human_bots_dataset.csv")

# Set list of IDs
account_ids = list(raw_df.id)

# Authenticate to tweepy
keys = ''
    
with open("config.yaml") as file:
    keys = yaml.safe_load(file)

client = tweepy.Client(bearer_token=keys["search_tweets_api"]["bearer_token"], wait_on_rate_limit=True)

now = datetime.datetime.utcnow()
i = 0

# Create .csv & write column headings
fields = ['id','account_type','account_age_days','verified','profile_image_url','followers_count','following_count','tweet_count','average_tweets_per_day','hour_created','network', 'tweet_to_followers', 'follower_acq_rate', 'friends_acq_rate']
filename = "twitter_dataset_expanded.csv"

with open(filename, 'w') as csvfile: 
    csvwriter = csv.writer(csvfile) 
    csvwriter.writerow(fields) 

# Loop through dataset
while i < raw_df.shape[0]:

    # Pull 99 Twitter users
    j = i + 99
    ids = raw_df[i:j]['id'].values
    ids = ids.tolist()
    users = client.get_users(ids=ids, user_fields="created_at,verified,public_metrics,description,profile_image_url")
    print("looking at ids: " + str(i) + "-" + str(ids[0]) + " and " + str(j) + "-" + str(ids[-1]))

    # Loop through Twitter users
    for user in users.data:
        if user.data is not None:
            account_age_days = (datetime.datetime.utcnow().replace(tzinfo=pytz.UTC) - parser.parse(user.data['created_at'])).days
            verified = user.data['verified']
            profile_image_url = user.data['profile_image_url']
            followers_count = user.data['public_metrics']['followers_count']
            following_count = user.data['public_metrics']['following_count']
            tweet_count = user.data['public_metrics']['tweet_count']
            average_tweets_per_day = np.round(tweet_count / account_age_days, 3)

            hour_created = parser.parse(user.data['created_at']).hour
            network = np.round(np.log(1 + following_count)* np.log(1 + followers_count), 3)
            tweet_to_followers = np.round(np.log(1 + tweet_count) * np.log(1 + followers_count), 3)
            follower_acq_rate = np.round(np.log(1 + (followers_count / account_age_days)), 3)
            friends_acq_rate = np.round(np.log(1 + (following_count / account_age_days)), 3)

            account_type = raw_df.loc[raw_df['id'] == int(user.data['id'])]
            row = [user.data['id'], account_type.values[0][1], account_age_days, verified, profile_image_url, followers_count, following_count, tweet_count, average_tweets_per_day, hour_created, network, tweet_to_followers, follower_acq_rate, friends_acq_rate]

            # Add expanded Twitter user to expanded .csv
            with open(filename, 'a') as csvfile: 
                csvwriter = csv.writer(csvfile) 
                csvwriter.writerow(row) 

    # Get the next 99 Twitter users
    i = i + 99

print("Done :)")