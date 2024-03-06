import random
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def predict_sentiment_v1(text: str):
    prediction = []
    for word in text.split():
        prediction.append(random.uniform(-1, 1))
    result = sum(prediction) / len(text.split())
    if result > 1/6:
        return 'Positive', round(result, 2)
    elif result < -1/6:
        return 'Negative', round(result, 2)
    else:
        return 'Neutral', round(result, 2)


def interpret_vader(score: float):
    if score <= -0.75:
        return 'Very Negative'
    elif score <= -0.25:
        return 'Negative'
    elif score <= -0.05:
        return 'Slightly Negative'
    elif score < 0.05:
        return 'Neutral'
    elif score < 0.25:
        return 'Slightly Positive'
    elif score < 0.75:
        return 'Positive'
    else:
        return 'Very Positive'


def predict_sentiment_vader(text: str):
    analyzer = SentimentIntensityAnalyzer()
    analysis = analyzer.polarity_scores(text)
    analysis['interpretation'] = interpret_vader(analysis['compound'])
    return analysis