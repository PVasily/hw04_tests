from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from ..models import Post, Group
from ..forms import PostForm


User = get_user_model()


class PostCreateFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='Anonimus')
        cls.form = PostForm()

    @classmethod
    def setUp(self):
        self.group = Group.objects.create(
            title='Test group',
            slug='test-slug',
            description='Test description')
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовый пост')
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_form(self):
        post_count = Post.objects.count()
        form_data = {
            'text': 'Новый текст из формы',
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            Post.objects.filter(
                text='Новый текст из формы').exists())

    def test_create_form_for_guest(self):
        """Проверяем редирект гостя при попытке зайти на страницу /create/."""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Текст из формы',
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, '/auth/login/?next=/create/')
        self.assertEqual(Post.objects.count(), post_count)
        self.assertEqual(response.status_code, 200)

    def test_post_edit(self):
        form_data = {
            'text': 'New text',
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.context['post'].text, 'New text')
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}))

    def test_form_label(self):
        field = PostCreateFormTest.form.fields
        dict_match = {
            f'{field["text"].label}': 'Текст поста',
            f'{field["group"].label}': 'Название сообщества',
            f'{field["text"].help_text}': 'Введите текст поста',
            f'{field["group"].help_text}': 'Выбирите группу'
        }
        for field, value in dict_match.items():
            self.assertEquals(field, value)
