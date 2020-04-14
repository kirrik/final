from django.test import TestCase, Client
from django.urls import reverse
from posts.models import Post
from django.contrib.auth import get_user_model

User = get_user_model()

class TestPosts(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='sarah', email='connor.s@skynet.com', password='12345')


    def test_profile_page(self):
        self.client.login(username='sarah', password='12345')
        response = self.client.get(f'/{self.user.username}/')
        self.assertEqual(response.status_code, 200)
