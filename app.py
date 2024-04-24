from flask import Flask, render_template, request, redirect, url_for
import requests
from textblob import TextBlob
import statistics
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
metrics = PrometheusMetrics(app)  # Create PrometheusMetrics instance

# Empty list to store comments
filtered_comments = []

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/process_comments', methods=['POST'])
def process_comments():
    global filtered_comments

    commentNumber = int(request.form['commentNumber'])
    videoId = request.form['videoId']

    url = f"https://www.googleapis.com/youtube/v3/commentThreads?key=AIzaSyAdiwelV4X32OUoQHAk4s8uFGQ8i3K2iGk&textFormat=plainText&part=snippet&videoId={videoId}&maxResults={commentNumber}"
    response = requests.get(url)
    data = response.json()

    # Get all the comments from the API response
    for item in data['items']:
        filtered_comments.append(item['snippet']['topLevelComment']['snippet']['textDisplay'])

    # Process and analyze the comments using TextBlob
    analysis_results = analysis(filtered_comments)

    # Redirect to the result page with the analysis_results parameter
    return redirect(url_for('result', analysis_results=analysis_results))

@app.route('/result')
def result():
    # Get the analysis results from the URL parameter
    analysis_results = request.args.get('analysis_results')

    if analysis_results is None:
        # Handle the case where analysis_results is not defined
        return "Error: Analysis results not available."

    # Return the sentiment analysis results here
    return render_template('result.html', analysis_results=analysis_results)

@metrics.do_not_track()
def analysis(filtered_comments):
    if not filtered_comments:
        return {"error": "No comments to analyze"}

    # Initialize sentiment counters
    sentiment_counts = {
        "positive": 0,
        "negative": 0,
        "neutral": 0
    }

    # Perform sentiment analysis for each comment
    sentiments = []
    for comment in filtered_comments:
        analysis = TextBlob(comment)
        polarity = analysis.sentiment.polarity

        if polarity > 0:
            sentiment_counts["positive"] += 1
        elif polarity < 0:
            sentiment_counts["negative"] += 1
        else:
            sentiment_counts["neutral"] += 1

        sentiments.append(polarity)

    # Calculate percentages
    total_comments = len(filtered_comments)
    positive_percentage = (sentiment_counts["positive"] / total_comments) * 100
    negative_percentage = (sentiment_counts["negative"] / total_comments) * 100
    neutral_percentage = (sentiment_counts["neutral"] / total_comments) * 100

    # Calculate overall sentiment score
    overall_sentiment_score = statistics.mean(sentiments)

    # Generate result dictionary
    analysis_results = {
        "sentiment_counts": sentiment_counts,
        "positive_percentage": positive_percentage,
        "negative_percentage": negative_percentage,
        "neutral_percentage": neutral_percentage,
        "overall_sentiment_score": overall_sentiment_score
    }

    return analysis_results

if __name__ == '__main__':
    app.run(debug=True)