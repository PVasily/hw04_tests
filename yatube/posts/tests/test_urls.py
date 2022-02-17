from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from ..models import Post, Group


User = get_user_model()


class StaticURLTests(TestCase):
    def test_homepage(self):
        guest_client = Client()
        response = guest_client.get('/')
        self.assertEqual(response.status_code, 200)


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='auth')
        PostURLTests.post = Post.objects.create(
            author=cls.user,
            text='Тестовая пост',
        )
        PostURLTests.group = Group.objects.create(
            title='Test group',
            slug='test-slug',
            description='Test description')
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_post_edit_url(self):
        """Страница по адресу / использует шаблон posts/index.html."""
        if self.authorized_client == self.post.author:
            response = self.authorized_client.get(
                f'/posts/{self.post.id}/edit/')
            self.assertEqual(response.status_code, 200)

    def test_post_create_url(self):
        """Страница по адресу / использует шаблон posts/index.html."""
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
