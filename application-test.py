import pytest
from unittest.mock import patch
from app import app, analysis
import uuid

@pytest.fixture
def client():
    """Create a test client for the app."""
    with app.test_client() as client:
        yield client

def generate_video_id():
    """Generate a random video ID."""
    return str(uuid.uuid4())  # Generate a random UUID and convert it to a string

def test_index_page(client):
    """Test if the index page returns a valid response."""
    response = client.get('/')
    assert response.status_code == 200

def test_process_comments(client):
    """Test if the process_comments route redirects properly."""
    video_id = generate_video_id()  # Generate a random video ID for testing
    with patch('prometheus_flask_exporter.metrics.request.prom_do_not_track', new=lambda: None):
        response = client.post('/process_comments', data={'commentNumber': '5', 'videoId': video_id})
    assert response.status_code == 302
    assert response.location.endswith('/result')

def test_result_page(client):
    """Test if the result page returns a valid response."""
    response = client.get('/result?analysis_results={}')
    assert response.status_code == 200

def test_analysis_no_comments():
    """Test analysis function with no comments."""
    with patch('prometheus_flask_exporter.metrics.request.prom_do_not_track', new=lambda: None):
        result = analysis([])
    assert result == {"error": "No comments to analyze"}