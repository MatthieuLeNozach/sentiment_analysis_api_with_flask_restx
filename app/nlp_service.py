from flask import Flask, request, jsonify
from nlp_sentiment import predict_sentiment_v1, predict_sentiment_vader


app = Flask(__name__)

@app.route('/predict/v1', methods=['POST'])
def predict_v1():
    data = request.get_json()
    text = data['text']
    sentiment, score = predict_sentiment_v1(text)
    return jsonify({'sentiment': sentiment, 'score': score})


@app.route('/predict/vader', methods=['POST'])
def predict_vader():
    data = request.get_json()
    text = data['text']
    analysis = predict_sentiment_vader(text)
    return jsonify({'sentiment': analysis})



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
