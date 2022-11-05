import asyncio
from tweepy.asynchronous import AsyncClient, AsyncPaginator


async def main():
    bearer_token = "***REMOVED***"

    client = AsyncClient(bearer_token)

    # This endpoint/method returns Tweets from the last seven days
    async for tweet in AsyncPaginator(client.search_recent_tweets, query="Tweepy", expansions = "author_id",  tweet_fields=['context_annotations', 'created_at'], max_results=100).flatten(limit=450):
        print(tweet.id)
        print(tweet.text)

asyncio.run(main())