from django.test import TestCase, Client
from django.urls import reverse
from posts.models import Post
from django.contrib.auth import get_user_model

User = get_user_model()

class TestPosts(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="sarah", email="connor.s@skynet.com", password="12345")


    def test_new_post(self):
        self.client.login(username='sarah', password='12345')
        response = self.client.get('/new/')
        self.assertEqual(response.status_code, 200)


    def test_not_auth_new(self):
        response = self.client.get('/new/')
        self.assertRedirects(response, '/auth/login/?next=/new/')

    
    def test_new_post_pub(self):
        self.client.login(username='sarah', password='12345')

        user = User.objects.get(username=self.user.username)
        post = Post.objects.create(text="Текст тестового поста", author=user)

        pages = (
            '',
            f'/{user.username}/',
            f'/{user.username}/{post.id}/'
        )

        for page in pages:
            response = self.client.get(page)
            self.assertContains(response, 'Текст тестового поста', status_code=200)


    def test_post_edit(self):
        self.client.login(username='sarah', password='12345')

        user = User.objects.get(username=self.user.username)
        post = Post.objects.create(text="Текст тестового поста 2", author=user)
        post_edit = self.client.post(f'/{post.author}/{post.id}/edit/', {'text':'Новый текст поста (ред.)'}, follow=True)

        pages = (
            '',
            f'/{user.username}/',
            f'/{user.username}/{post.id}/'
        )

        for page in pages:
            response = self.client.get(page)
            self.assertContains(response, 'Новый текст поста (ред.)', status_code=200)


    def test_404_error_page(self):
        response = self.client.get('/abrakadabra/')
        self.assertEqual(response.status_code, 404)


    def test_post_with_img(self):
        self.client.login(username='sarah', password='12345')

        user = User.objects.get(username=self.user.username)
        post = Post.objects.create(text="Текст тестового поста 777", author=user)
        with open('media\posts\leo.jpg', 'rb') as fp:
            self.client.post(f'/{user.username}/{post.id}/edit/', {'text':'fred', 'image':fp})

        response = self.client.get(f'/{user.username}/{post.id}/')
        self.assertContains(response, '<img', status_code=200)


    def test_post_with_img_pages(self):
        self.client.login(username='sarah', password='12345')

        user = User.objects.get(username=self.user.username)
        post = Post.objects.create(text="Текст тестового поста 777", author=user)
        with open('media\posts\leo.jpg', 'rb') as fp:
            self.client.post(f'/{user.username}/{post.id}/edit/', {'text':'fred', 'image':fp})
        
        pages = (
            '',
            f'/{user.username}/',
            f'/{user.username}/{post.id}/'
        )

        for page in pages:
            response = self.client.get(page)
            self.assertContains(response, '<img', status_code=200)


    def test_upload_not_img_file(self):
        self.client.login(username='sarah', password='12345')

        user = User.objects.get(username=self.user.username)
        post = Post.objects.create(text="Текст тестового поста 777", author=user)
        with open('media\posts\kirrik.txt', 'rb') as fp:
            response = self.client.post(f'/{user.username}/{post.id}/edit/', {'text':'fred', 'image':fp})
        
        self.assertFalse(response.context['form'].is_valid())

