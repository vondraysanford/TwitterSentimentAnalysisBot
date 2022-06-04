import datetime
import numpy as np
import pickle
import pytz
import tweepy
import yaml


def auth_to_tweepy():
    keys = ''
    
    # Get keys from .yaml file
    with open("config.yaml") as file:
        keys = yaml.safe_load(file)

    # Initialize client
    client = tweepy.Client(keys["search_tweets_api"]["bearer_token"])
    return client

def get_xbg_model():
    with open('model.pickle', 'rb') as read_file:
        xgb_model = pickle.load(read_file)
        return xgb_model

def get_user_info(client, id):
    user = client.get_user(id=id, user_fields="created_at,verified,public_metrics,description,profile_image_url")

    if user.data is not None:

        account_age_days = (datetime.datetime.utcnow().replace(tzinfo=pytz.UTC) - user.data['created_at']).days

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
        bot_probability = np.round(xgb_model.predict_proba(user)[:, 1][0]*100, 2) # Unicode-9 is not supported.
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

def main():
    client = auth_to_tweepy()
    user_features = get_user_info(client, 19660870)
    xgb_model = get_xbg_model()
    probability = get_bot_probability(user_features, xgb_model)
    result = get_result(probability)
    print(result)
    
if __name__ == "__main__":
    main()