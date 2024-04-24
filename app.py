from flask import Flask, render_template, request, redirect, url_for
import requests
from textblob import TextBlob
import statistics

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/process_comments', methods=['POST'])
def process_comments():
    commentNumber = int(request.form['commentNumber'])
    videoId = request.form['videoId']

    url = f"https://www.googleapis.com/youtube/v3/commentThreads?key=AIzaSyAdiwelV4X32OUoQHAk4s8uFGQ8i3K2iGk&textFormat=plainText&part=snippet&videoId={videoId}&maxResults={commentNumber}"
    response = requests.get(url)
    data = response.json()

    if 'items' in data:
        filtered_comments = [item['snippet']['topLevelComment']['snippet']['textDisplay'] for item in data['items']]
        analysis_results = analysis(filtered_comments)
        return redirect(url_for('result', analysis_results=analysis_results))
    else:
        error_message = "Error: No comments found for the provided video ID."
        return redirect(url_for('result', analysis_results=error_message))

@app.route('/result')
def result():
    analysis_results = request.args.get('analysis_results')

    if analysis_results is None:
        return "Error: Analysis results not available."

    return render_template('result.html', analysis_results=analysis_results)

def analysis(filtered_comments):
    polarities = [TextBlob(comment).sentiment.polarity for comment in filtered_comments]

    positive = sum(polarity > 0 for polarity in polarities)
    wpositive = sum(0 < polarity <= 0.3 for polarity in polarities)
    spositive = sum(0.3 < polarity <= 0.6 for polarity in polarities)
    negative = sum(polarity < 0 for polarity in polarities)
    wnegative = sum(-0.3 < polarity <= 0 for polarity in polarities)
    snegative = sum(-0.6 < polarity <= -0.3 for polarity in polarities)
    neutral = sum(polarity == 0 for polarity in polarities)

    total_comments = len(filtered_comments)

    positive_percentage = format(100 * positive / total_comments, '.2f')
    wpositive_percentage = format(100 * wpositive / total_comments, '.2f')
    spositive_percentage = format(100 * spositive / total_comments, '.2f')
    negative_percentage = format(100 * negative / total_comments, '.2f')
    wnegative_percentage = format(100 * wnegative / total_comments, '.2f')
    snegative_percentage = format(100 * snegative / total_comments, '.2f')
    neutral_percentage = format(100 * neutral / total_comments, '.2f')

    sentiment_scores = [polarity for polarity in polarities if polarity != 0]
    if sentiment_scores:
        overall_score = statistics.mean(sentiment_scores)
        if overall_score > 0:
            sentiment_result = f"Overall sentiment: Positive with Score {format(100 * overall_score, '.2f')}%"
        elif overall_score < 0:
            sentiment_result = f"Overall sentiment: Negative with Score {format(100 * overall_score, '.2f')}%"
        else:
            sentiment_result = f"Overall sentiment: Neutral with Score 0.00%"
    else:
        sentiment_result = "No sentiment detected."

    detailed_report = (
        f"Positive: {positive_percentage}%, "
        f"Weakly Positive: {wpositive_percentage}%, "
        f"Strongly Positive: {spositive_percentage}%, "
        f"Negative: {negative_percentage}%, "
        f"Weakly Negative: {wnegative_percentage}%, "
        f"Strongly Negative: {snegative_percentage}%, "
        f"Neutral: {neutral_percentage}%"
    )

    return f"{sentiment_result}\n\n{detailed_report}"

if __name__ == '__main__':
    app.run(debug=True)
