import requests
import os
from textblob import TextBlob
from dotenv import load_dotenv

load_dotenv()
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

def get_sentiment(ticker):
    try:
        url = f"https://newsapi.org/v2/everything?q={ticker}&language=en&pageSize=5&apiKey={NEWS_API_KEY}"
        response = requests.get(url).json()

        print("API Status:", response.get('status'))
        print("Total Results:", response.get('totalResults'))

        articles = response.get('articles', [])

        if not articles:
            return "🟡 Neutral", 0.0, []

        # Return full article info (title + description)
        news_data = []
        for a in articles:
            news_data.append({
                "title": a.get('title', ''),
                "description": a.get('description', 'No details available.'),
                "url": a.get('url', '')
            })

        scores = [TextBlob(a['title']).sentiment.polarity for a in news_data]
        avg_score = sum(scores) / len(scores) if scores else 0

        if avg_score > 0.1:
            sentiment = "🟢 Positive"
        elif avg_score < -0.1:
            sentiment = "🔴 Negative"
        else:
            sentiment = "🟡 Neutral"

        return sentiment, avg_score, news_data

    except Exception as e:
        return "🟡 Neutral", 0.0, []