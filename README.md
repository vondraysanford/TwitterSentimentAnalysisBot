# 🐦 Twitter Sentiment Analysis & Bot Detection

A Python-based NLP pipeline that analyzes tweet sentiment and detects bot accounts using machine learning, integrated with a Discord bot for real-time interaction.

---

## Overview

This project combines **natural language processing**, **machine learning classification**, and **cryptographic model verification** into an end-to-end sentiment analysis system. It pulls tweets via the Twitter API, classifies their sentiment using a trained model, identifies potential bot accounts, and surfaces results through a custom Discord bot.

## Key Features

- **Sentiment Classification** — Analyzes tweet text for positive, negative, and neutral sentiment using TextBlob and a custom-trained model
- **Bot Detection** — Identifies automated/bot Twitter accounts using XGBoost classification
- **Model Integrity Verification** — Signs and verifies serialized model files using RSA cryptographic signatures
- **Discord Integration** — Real-time sentiment queries through a Discord bot built with discord.py
- **Data Pipeline** — Automated dataset expansion, model training, and evaluation workflow

## Tech Stack

| Category | Technologies |
|---|---|
| **Language** | Python 3 |
| **NLP & ML** | NLTK, TextBlob, Scikit-learn, XGBoost, TensorFlow |
| **Data & Visualization** | pandas, NumPy, Matplotlib, Seaborn, Plotly |
| **APIs & Integration** | Tweepy (Twitter API v2), discord.py, aiohttp |
| **Security** | Cryptography (RSA signing/verification) |
| **Other** | pytz, PyYAML, WordCloud |

## Architecture

```
Twitter API (Tweepy)
    │
    ▼
GenerateExpandedTwitterDataset.py   ──►   Raw tweet data
    │
    ▼
GenerateModel.ipynb                 ──►   Trained ML model (.pkl)
    │
    ▼
SignPickle.py / VerifyPickle.py     ──►   Signed & verified model
    │
    ▼
TweetSentimentAnalysis.py           ──►   Sentiment predictions
    │
    ▼
Discord Bot (discord.py)            ──►   User-facing interface
```

## Getting Started

### Prerequisites

- Python 3.8+
- Twitter Developer Account with API keys ([developer.twitter.com](https://developer.twitter.com/en))
- Discord Developer Application with bot token ([discord.com/developers](https://discord.com/developers/applications))

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/twitter-sentiment-analysis.git
   cd twitter-sentiment-analysis
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure API credentials — add your Twitter API keys and Discord bot token to your environment or config file.

### Usage

1. **Generate the dataset:**
   ```bash
   python GenerateExpandedTwitterDataset.py
   ```

2. **Train the model:**
   Open and run `GenerateModel.ipynb` in Jupyter.

3. **Sign and verify the model:**
   ```bash
   python SignPickle.py
   python VerifyPickle.py
   ```

4. **Run sentiment analysis:**
   ```bash
   python TweetSentimentAnalysis.py
   ```

5. **Launch the Discord bot:**
   ```bash
   python bot.py
   ```

## Datasets

- [Amazon Fine Food Reviews](https://www.kaggle.com/datasets/snap/amazon-fine-food-reviews?select=Reviews.csv) — used for supplemental sentiment training data
- [Twitter Bots Accounts](https://www.kaggle.com/datasets/davidmartngutirrez/twitter-bots-accounts) — used for bot detection model training

## Acknowledgments

This project was built with guidance from several tutorials and resources. See the references below for the key sources that informed the approach.

<details>
<summary><strong>References & Resources</strong></summary>

- [How to Analyze the Sentiment of Your Own Tweets](https://developer.twitter.com/en/docs/tutorials/how-to-analyze-the-sentiment-of-your-own-tweets) — Twitter Developer Docs
- [A Beginner's Guide to Sentiment Analysis with Python](https://towardsdatascience.com/a-beginners-guide-to-sentiment-analysis-in-python-95e354ea84f6) — Towards Data Science
- [Sentiment Analysis using Python](https://techvidvan.com/tutorials/python-sentiment-analysis/) — TechVidvan
- [Twitter Sentiment Analysis & Botometer](https://medium.com/analytics-vidhya/twitter-sentiment-analysis-botometer-part-2-aecdbbbada30) — Analytics Vidhya
- [Twitter Bot or Not](https://scrapfishies.medium.com/twitter-bot-or-not-cc2ad52b36ba) — Medium
- [Python String Signing using Cryptography](https://www.cryptoexamples.com/python_cryptography_string_signature_rsa.html)
- [discord.py Examples](https://github.com/Rapptz/discord.py/tree/master/examples)

</details>

---

*Built with Python, curiosity, and a healthy skepticism of Twitter bots.*
