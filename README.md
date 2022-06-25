# Twitter Sentiment Analysis Bot
This discord bot is for analyzing the sentiment of tweets on Twitter.

# Next Steps:
1. Split functionality into eight hour (8 a.m. to 4 p.m.) session, hourly & on command analysis
1. Implement Discord.py
1. Implement slash commands with (Dislash) https://github.com/EQUENOS/dislash.py or full rewrite with (Disnake) https://docs.disnake.dev/en/latest/

# Helpful Links
- (Cheatsheet for creating this lol) - https://markdown.land/markdown-cheat-sheet
- GeeksForGeeks - https://www.geeksforgeeks.org/
- Amazon Fine Food Reviews Dataset - https://www.kaggle.com/datasets/snap/amazon-fine-food-reviews?select=Reviews.csv
- pandas - https://pypi.org/project/pandas/#description
- Matplotlib - https://matplotlib.org/stable/index.html
- Objectivity vs Subjectivity - https://www.youtube.com/watch?v=4O45mRHMzpw
- Twitter Bots Accounts Dataset - https://www.kaggle.com/datasets/davidmartngutirrez/twitter-bots-accounts
- pytz - https://pythonhosted.org/pytz/
- seaborn - https://seaborn.pydata.org/
- NumPy - https://numpy.org/
- Crypto Markets Trading Hours Converter - https://www.finder.com/crypto-markets-trading-hours-converter

# Examples
## Example 1
How to analyze the sentiment of your own Tweets -> https://developer.twitter.com/en/docs/tutorials/how-to-analyze-the-sentiment-of-your-own-tweets
### Relevant Documentation
- Determining Tweet types -> https://developer.twitter.com/en/docs/tutorials/determining-tweet-types
- yaml - https://pyyaml.org/

## Example 2
A Beginner’s Guide to Sentiment Analysis with Python -> https://towardsdatascience.com/a-beginners-guide-to-sentiment-analysis-in-python-95e354ea84f6
### Relevant Documentation
- Plotly - https://plotly.com/python/getting-started/
- NLTK - https://www.nltk.org/
- word_cloud - https://github.com/amueller/word_cloud
- Scikit-learn - https://scikit-learn.org/stable/index.html

## Example 3
3. Sentiment Analysis using Python -> https://techvidvan.com/tutorials/python-sentiment-analysis/
### Relevant Documentation
- TensorFlow - https://www.tensorflow.org/

## Example 4
4. (DO THIS ONE) Twitter Sentiment Analysis & Botometer (Part 2) -> https://medium.com/analytics-vidhya/twitter-sentiment-analysis-botometer-part-2-aecdbbbada30
### Relevant Documentation
- Tweepy - https://docs.tweepy.org/en/latest/index.html
- Tweepy Help - https://dev.to/twitterdev/a-comprehensive-guide-for-using-the-twitter-api-v2-using-tweepy-in-python-15d9
- Text Blob - https://textblob.readthedocs.io/en/dev/

## Example 5
5. Twitter Bot or Not -> https://scrapfishies.medium.com/twitter-bot-or-not-cc2ad52b36ba
### Relevant Documentation
- XGBoost - https://xgboost.readthedocs.io/en/stable/index.html

## Example 6
6. Python String Signing using Cryptography -> https://www.cryptoexamples.com/python_cryptography_string_signature_rsa.html
### Relevant Documentation
- Explanation of Public/Private Keys & Signing -> https://blog.todotnet.com/2018/02/public-private-keys-and-signing/
- Cryptography - https://cryptography.io/en/latest/
- Help - https://stackoverflow.com/questions/50608010/how-to-verify-a-signed-file-in-python

# Steps
1. Make a Twitter Account -> https://twitter.com/i/flow/signup
1. Create a Twitter Bot -> https://developer.twitter.com/en
1. Create a Postman Account for API Testing -> https://identity.getpostman.com/signup
1. Take keys and integrate with tutorials -> https://developer.twitter.com/en/docs/tutorials?filter=/product/twitter-api
1. Once comfortable, view the examples in the **Examples** section, make sure you understand them.
1. Run GenerateExpandedTwitterDataset.py **THEN ->** GenerateModel.ipynb
1. Run SignPickle.py and VerifyPickle.py to generate/test keys & signature
1. Test TweetSentimentAnalysis.py & TwitterAccountBotAnalysis.py and combine processes.