# 🐦 Twitter Sentiment Analysis & Bot Detection

A production-ready Python pipeline that analyzes tweet sentiment and detects bot accounts using machine learning, with real-time Discord bot integration.

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🎯 Project Overview

This end-to-end NLP system combines **sentiment analysis**, **bot detection**, and **cryptographic model verification** into a production-ready application. It demonstrates expertise in:

- **Machine Learning** — Training and deploying XGBoost classifiers for binary classification (bot/human)
- **NLP** — Text processing with NLTK, TextBlob for sentiment scoring, and feature engineering
- **API Integration** — Twitter API v2 (Tweepy), Discord.py for real-time bot interaction
- **Security** — RSA cryptographic signatures for model integrity verification
- **Software Engineering** — Modular architecture, data pipelines, configuration management

### Key Capabilities

| Feature | Description |
|---------|-------------|
| **Sentiment Classification** | Analyzes tweet polarity (positive/negative/neutral) using TextBlob and trained ML models |
| **Bot Detection** | Identifies automated Twitter accounts with 13-feature XGBoost classifier |
| **Model Verification** | Cryptographic RSA signatures ensure model integrity and prevent tampering |
| **Discord Integration** | Real-time sentiment queries through interactive Discord commands |
| **Data Pipeline** | Automated workflow: data collection → feature engineering → model training → deployment |

---

## 🏗️ Architecture

```
┌─────────────────┐
│  Twitter API    │ (Tweepy - API v2)
│  (Real tweets)  │
└────────┬────────┘
         │
         ▼
    ┌────────────────────────────────────────┐
    │ GenerateExpandedTwitterDataset.py      │ Extract user metrics & tweet data
    │ (13 features: followers, verified, etc)│
    └────────┬───────────────────────────────┘
             │
             ▼
    ┌────────────────────────────────────┐
    │ GenerateModel.ipynb                │ Train XGBoost classifier
    │ (Amazon Reviews + Twitter data)    │ Test with multiple algorithms
    └────────┬───────────────────────────┘
             │
             ▼
    ┌────────────────────────────────────┐
    │ SignPickle.py / VerifyPickle.py   │ RSA-sign model.pickle
    │ (Cryptography - model security)    │ Prevent unauthorized modifications
    └────────┬───────────────────────────┘
             │
             ▼
    ┌────────────────────────────────────┐
    │ TweetSentimentAnalysis.py          │ Load & verify signed model
    │ (Production inference)             │ Classify new tweets/users
    └────────┬───────────────────────────┘
             │
             ▼
    ┌────────────────────────────────────┐
    │ Discord Bot (discord.py)           │ User-facing CLI interface
    │ (Real-time predictions)            │ Real-time sentiment queries
    └────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Category | Technologies |
|----------|---------------|
| **Language** | Python 3.8+ |
| **ML & NLP** | XGBoost, Scikit-learn, TensorFlow, NLTK, TextBlob |
| **Data Processing** | pandas, NumPy, Matplotlib, Seaborn, Plotly, WordCloud |
| **APIs & Integration** | Tweepy (Twitter API v2), discord.py, aiohttp |
| **Security & Cryptography** | cryptography (RSA), PyYAML |
| **Utilities** | pytz (timezone handling), pickle (model serialization) |

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.8+**
- **Twitter Developer Account** — [Get API Keys](https://developer.twitter.com/en)
  - Requires API v2 credentials (Bearer Token)
  - Apply for [Academic Research](https://developer.twitter.com/en/products/twitter-api/academic-research) or [Standard](https://developer.twitter.com/en/products/twitter-api/starter-pack) access
  
- **Discord Developer Account** — [Create Bot Application](https://discord.com/developers/applications)
  - Create a new application → Bot → Copy token
  
- **Git** (for cloning the repository)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/vondraysanford/TwitterSentimentAnalysisBot.git
   cd TwitterSentimentAnalysisBot
   ```

2. **Create and activate a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API Credentials:**
   ```bash
   # Copy the example config
   cp Resources/Config.example.yaml Resources/Config.yaml
   ```
   
   Edit `Resources/Config.yaml` and add your credentials:
   ```yaml
   discord_api:
     client: "YOUR_DISCORD_BOT_TOKEN_HERE"
   
   search_tweets_api:
     bearer_token: "YOUR_TWITTER_BEARER_TOKEN_HERE"
   ```
   
   ⚠️ **Security:** 
   - Never commit `Config.yaml` to version control
   - It's already listed in `.gitignore` to prevent accidental credential leaks
   - Generate new tokens if this repo was ever public with real credentials

---

## 📖 Usage Guide

### 1. Generate Training Dataset

Extract user metrics and tweet data from Twitter:

```bash
python Scripts/GenerateExpandedTwitterDataset.py
```

**Output:** `Resources/twitter_human_bots_dataset.csv` with 17 engineered features:
- Account age, verification status, follower/following counts
- Tweet frequency, network metrics, acquisition rates

### 2. Train the Model

Open and run the notebook:

```bash
jupyter notebook Scripts/GenerateModel.ipynb
```

**What it does:**
- Loads Amazon Fine Food Reviews (sentiment labels) and Twitter bot dataset
- Tests multiple ML algorithms (XGBoost, TensorFlow LSTM, etc.)
- Evaluates using accuracy, precision, recall, F1-score
- Saves best model as `Resources/model.pickle`

### 3. Secure the Model with Cryptography

Sign the serialized model using RSA:

```bash
python Scripts/SignPickle.py      # Generates signature.sig
python Scripts/VerifyPickle.py    # Validates signature
```

**Purpose:** Ensures model hasn't been tampered with before deployment.

### 4. Run Sentiment Analysis

Analyze tweets and user accounts:

```bash
python Scripts/TweetSentimentAnalysis.py
```

### 5. Launch Discord Bot

Start the bot for real-time interaction:

```bash
python sentimentbot.py
```

**Discord Commands:**
- `!sentiment <query>` — Analyze tweet sentiment
- `!analyze <user_id>` — Detect if a user is likely a bot

---

## 📊 Key Features Deep Dive

### Sentiment Analysis
- **TextBlob:** Quick polarity & subjectivity scoring
- **Custom Model:** Trained on Amazon reviews + Twitter data
- **Output:** Positive/Negative/Neutral classification with confidence

### Bot Detection
**13 Feature Engineering:**
- Account age, verification status, default profile image
- Follower/following counts, tweet frequency
- Network metrics: `log(followers) * log(following)`
- Acquisition rates: `log(followers / account_age_days)`

**Model:** XGBoost binary classifier with 200 boosted trees

### Model Security
- **RSA Signatures:** Signs model.pickle with private key
- **Verification:** Public key verification on model load
- **Purpose:** Prevents model poisoning/tampering attacks

### Discord Integration
- **Real-time queries** without restarting
- **Async operations** using `discord.py` tasks
- **Rate limiting:** Respects Twitter API rate limits with automatic backoff

---

## 📁 Project Structure

```
TwitterSentimentAnalysisBot/
├── Resources/
│   ├── Config.example.yaml           # Template for API credentials
│   ├── Config.yaml                   # (gitignored) Your actual credentials
│   ├── model.pickle                  # Trained XGBoost classifier
│   ├── signature.sig                 # RSA signature for model
│   ├── pubkey.cer                    # Public key for verification
│   └── twitter_human_bots_dataset.csv # Training data
├── Scripts/
│   ├── GenerateExpandedTwitterDataset.py  # Data collection & feature engineering
│   ├── GenerateModel.ipynb                # Model training notebook
│   ├── SignPickle.py                      # Sign model with RSA
│   ├── VerifyPickle.py                    # Verify model signature
│   └── TweetSentimentAnalysis.py          # Inference pipeline
├── Examples/
│   ├── TwitterAPIExample.py               # Twitter API usage
│   ├── TweetSentimentAnalysisExample.py   # Sentiment analysis demo
│   └── SentimentAnalysisExample2.ipynb    # LSTM training notebook
├── sentimentbot.py                        # Discord bot main file
├── requirements.txt                       # Python dependencies
├── .gitignore                             # Security: excludes Config.yaml
└── README.md                              # This file
```

---

## 🔬 Technical Highlights

### Machine Learning Pipeline
- **Dataset:** 50K+ Amazon reviews + 5K+ Twitter accounts
- **Feature Engineering:** 13 computed features from API responses
- **Model Selection:** Tested XGBoost, TensorFlow LSTM, Scikit-learn classifiers
- **Hyperparameter Tuning:** Grid search for optimal XGBoost parameters
- **Evaluation:** Stratified k-fold cross-validation, ROC-AUC curves

### Cryptographic Security
```python
# Model integrity verification
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

public_key.verify(
    signature=signature,
    data=model_bytes,
    padding=padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.MAX_LENGTH
    ),
    algorithm=hashes.SHA256()
)
```

### API Integration
- **Tweepy v2:** Async-ready for high-volume data collection
- **Rate Limiting:** Automatic backoff with `wait_on_rate_limit=True`
- **Discord.py v2:** Modern async/await syntax, task scheduling

---

## 📚 Datasets Used

| Dataset | Source | Purpose |
|---------|--------|---------|
| Amazon Fine Food Reviews (50K+) | [Kaggle](https://www.kaggle.com/datasets/snap/amazon-fine-food-reviews) | Sentiment labels for model training |
| Twitter Bots Accounts (5K+) | [Kaggle](https://www.kaggle.com/datasets/davidmartngutirrez/twitter-bots-accounts) | Bot detection training & validation |
| Real Twitter Data | Twitter API v2 | Live inference on current tweets |

---

## 🔐 Security Considerations

- **API Keys:** Use environment variables or config files (never hardcode)
- **Model Integrity:** RSA signatures verify model hasn't been poisoned
- **Rate Limiting:** Twitter API enforces limits; code handles gracefully
- **Data Privacy:** Only collect public tweets/user metrics

---

## 💡 Learning Outcomes

This project demonstrates:

✅ **Machine Learning:** Model training, feature engineering, hyperparameter tuning  
✅ **NLP:** Sentiment analysis, text preprocessing, tokenization  
✅ **API Integration:** RESTful APIs (Twitter v2), webhook patterns (Discord)  
✅ **Cryptography:** RSA signatures, key management, model verification  
✅ **Software Engineering:** Modular code, error handling, async programming  
✅ **Data Engineering:** ETL pipelines, feature computation, data validation  
✅ **DevOps:** Environment configuration, secrets management, CI/CD ready  

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| `Config.yaml not found` | Run `cp Resources/Config.example.yaml Resources/Config.yaml` and add credentials |
| `InvalidSignature on model load` | Regenerate signature: `python Scripts/SignPickle.py` |
| `Twitter API rate limit exceeded` | Wait 15 minutes or upgrade to Academic Research track |
| `Discord bot offline` | Check bot token is valid and has correct permissions |

---

## 📝 References & Resources

<details>
<summary><strong>Click to expand references</strong></summary>

- [Twitter API v2 Documentation](https://developer.twitter.com/en/docs/twitter-api)
- [How to Analyze Tweet Sentiment](https://developer.twitter.com/en/docs/tutorials/how-to-analyze-the-sentiment-of-your-own-tweets)
- [Sentiment Analysis with Python](https://towardsdatascience.com/a-beginners-guide-to-sentiment-analysis-in-python-95e354ea84f6)
- [XGBoost Documentation](https://xgboost.readthedocs.io/)
- [discord.py Documentation](https://discordpy.readthedocs.io/)
- [Cryptography & RSA Signatures](https://www.cryptoexamples.com/python_cryptography_string_signature_rsa.html)
- [Feature Engineering for Classification](https://machinelearningmastery.com/feature-engineering-for-machine-learning/)
- [Twitter Bot Detection Techniques](https://medium.com/analytics-vidhya/twitter-sentiment-analysis-botometer-part-2-aecdbbbada30)

</details>

---

## 📄 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) file for details.

---

## 📧 Contact & Questions

For questions about this project or to discuss its implementation:
- **GitHub:** [@vondraysanford](https://github.com/vondraysanford)
- **LinkedIn:** [https://www.linkedin.com/in/vondray-sanford/]

---

**Built with Python, machine learning, and a healthy skepticism of Twitter bots.** 🤖

*Last Updated: June 2024*
