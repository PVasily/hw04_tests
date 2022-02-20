from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from ..models import Post, Group


User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='author')
        cls.admin = User.objects.create(username='admin')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая пост',
        )
        cls.group = Group.objects.create(
            title='Test group',
            slug='test-slug',
            description='Test description')
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.auth_admin = Client()
        cls.auth_admin.force_login(cls.admin)

    def test_homepage(self):
        guest_client = Client()
        response = guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_post_edit_url(self):
        response = self.authorized_client.get(
            f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, 200)

    def test_post_edit_auth_not_author(self):
        response = self.auth_admin.get(
            f'/posts/{self.post.id}/edit/')
        self.assertRedirects(response, f'/posts/{self.post.id}/')

    def test_post_edit_guest(self):
        response = self.guest_client.get(
            f'/posts/{self.post.id}/edit/')
        self.assertRedirects(response, '/auth/login/?next=/posts/1/edit/')

    def test_post_create_url(self):
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_guest_urls(self):
        dict_match = {
            f'/group/{self.group.slug}/': 200,
            f'/posts/{self.post.id}/': 200,
            '/': 200,
            '/unexpected-page/': 404,
            f'/profile/{self.user.username}/': 200
        }
        for url, status_code in dict_match.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_create_page_url_redirect_anonymous_on_login(self):
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/create/')
