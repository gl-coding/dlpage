from django.test import TestCase, Client
from .models import DataPost

# Create your tests here.

class DataPostTest(TestCase):
    def test_post_data(self):
        client = Client()
        response = client.post('/datapost/', data='{"test": "value"}', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(DataPost.objects.count(), 1)
