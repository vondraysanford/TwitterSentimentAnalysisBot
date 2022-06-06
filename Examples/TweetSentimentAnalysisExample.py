import pandas as pd
import tweepy
import yaml

from textblob import TextBlob

def auth_to_tweepy():
    keys = ''
    
    with open("Resources/Config.yaml") as file:
        keys = yaml.safe_load(file)

    client = tweepy.Client(keys["search_tweets_api"]["bearer_token"])
    return client

def get_tweets_by_keyword(client, keyword):    
    tweet_id = []
    tweet_time = []
    tweet_string = []
    polarity_score = []
    subjectivity_score = []

    # Replace the limit=1000 with the maximum number of Tweets you want
    for tweet in tweepy.Paginator(client.search_recent_tweets, query=keyword, tweet_fields=['context_annotations', 'created_at'], max_results=100).flatten(limit=1000):
        if ("RT @" not in tweet.text):
            # Tweet's ID
            tweet_id.append(tweet.id)
            # Date and Time tweet was created
            tweet_time.append(tweet.created_at)
            # Actual tweet
            tweet_string.append(tweet.text)

            #Sentiment Analysis -> Polarity = -/+[-1,1] & Subjectivitiy = fact/feeling[0,1]
            polarity_score.append(TextBlob(tweet.text).sentiment.polarity)
            subjectivity_score.append(TextBlob(tweet.text).sentiment.subjectivity)

    # Creating dataframe with desired info
    dataframe = pd.DataFrame({'id':tweet_id, 'time': tweet_time, 'tweet': tweet_string, 'polarity': polarity_score, 'subjectivity': subjectivity_score})
    
    return dataframe

def get_sentiment(dataframe):
    sentiment_score = dataframe['polarity'].mean()

    if sentiment_score > 0.75 or sentiment_score == 0.75:
        return "Sentiment is positive"
    elif sentiment_score > 0.45 or sentiment_score == 0.45:
        return "Sentiment is neurtral"
    else:
        return "Sentiment is negative"

def main():
    client = auth_to_tweepy()
    dataframe = get_tweets_by_keyword(client, "cryptocurrency")
    sentiment = get_sentiment(dataframe)
    print(sentiment)
    
if __name__ == "__main__":
    main()