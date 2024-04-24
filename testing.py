import unittest
from app import app

class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_index_route(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_process_comments_route(self):
        response = self.app.post('/process_comments', data={'commentNumber': '10', 'videoId': 'YOUR_VIDEO_ID'})
        self.assertEqual(response.status_code, 302)  # Redirects to result route

    def test_result_route(self):
        response = self.app.get('/result')
        self.assertEqual(response.status_code, 200)

    def test_analysis_no_comments(self):
        analysis_results = analysis([])
        self.assertEqual(analysis_results, {"error": "No comments to analyze"})

    # Add more test cases as needed...

if __name__ == '__main__':
    unittest.main()
