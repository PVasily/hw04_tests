from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django import forms

from ..models import Post, Group


User = get_user_model()


class StaticURLTests(TestCase):
    def test_homepage(self):
        # Создаем экземпляр клиента
        guest_client = Client()
        # Делаем запрос к главной странице и проверяем статус
        response = guest_client.get('/')
        # Утверждаем, что для прохождения теста код должен быть равен 200
        self.assertEqual(response.status_code, 200)


class PostTemplatesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создадим запись в БД для проверки доступности адреса task/test-slug/
        cls.user = User.objects.create(username='auth')

        PostTemplatesTests.group = Group.objects.create(
            title='Test group',
            slug='test-slug',
            description='Test description'
        )

        PostTemplatesTests.post = Post.objects.create(
            id=1,
            author=cls.user,
            text='Тестовый пост',
            group=PostTemplatesTests.group
        )

        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_used_templates(self):
        """Сравнивает соответствие url-адресов используемым шаблонам."""

        dict_match = {
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}): 'posts/group_list.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}): 'posts/post_detail.html',
            '/': 'posts/index.html',
            reverse(
                'posts:profile',
                kwargs={
                    'username': self.user.username}): 'posts/profile.html',
            reverse(
                'posts:post_edit',
                 kwargs={'post_id': self.post.id}): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html'
        }
        for address, template in dict_match.items():
            with self.subTest(address=address):
                if self.authorized_client:
                    response = self.authorized_client.get(address)
                    self.assertTemplateUsed(response, template)
                elif self.authorized_client == self.post.author:
                    response = self.authorized_client.get(address)
                    self.assertTemplateUsed(response, template)
                else:
                    response = self.guest_client.get(address)
                    self.assertTemplateUsed(response, template)

    def test_types_fields_forms(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_types_fields_forms_post_edit(self):
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': 1}))
        if self.authorized_client == self.post.author:
            form_fields = {
                'text': forms.fields.CharField,
                'group': forms.fields.ChoiceField
            }
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context.get('form').fields.get(value)
                    self.assertIsInstance(form_field, expected)

    def test_index_page_show_correct_context(self):
        response = self.guest_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        first_text_0 = first_object.text
        first_group_0 = first_object.group.title
        self.assertEqual(first_text_0, 'Тестовый пост')
        self.assertEqual(first_group_0, self.group.title)


class PaginatorTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='Anonimus')
        cls.guest_client = Client()
        PaginatorTest.group = Group.objects.create(
            title='Test group',
            slug='test-slug',
            description='Test description')
        cls.posts = []
        for i in range(13):
            PaginatorTest.post = Post.objects.create(
                id=i,
                author=cls.user,
                text=f'Тестовый пост{i}',
                group=PaginatorTest.group)
            cls.posts.append(PaginatorTest.post)

    def test_paginator(self):
        slug = PaginatorTest.group.slug
        username = self.user.username
        dict_address = {
            '/?page=1': 10,
            f'/group/{slug}/?page=1': 10,
            f'/profile/{username}/?page=1': 10,
            '/?page=2': 3,
            f'/group/{slug}/?page=2': 3,
            f'/profile/{username}/?page=2': 3
        }
        for address, num in dict_address.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                len_page = len(response.context['page_obj'])
                self.assertEqual(len_page, num)


class ContextTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='Anonimus')
        cls.admin = User.objects.create(username='admin')
        ContextTest.group_one = Group.objects.create(
            title='Test group one',
            slug='test-slug_one',
            description='Test description')
        ContextTest.group_two = Group.objects.create(
            title='Test group two',
            slug='test-slug_two',
            description='Test description')
        cls.posts = []
        for i in range(13):
            if i % 2 == 0:
                ContextTest.post = Post.objects.create(
                    id=i,
                    author=cls.user,
                    text=f'Тестовый пост{i}',
                    group=ContextTest.group_one)
                cls.posts.append(ContextTest.post)
            else:
                ContextTest.post = Post.objects.create(
                    id=i,
                    author=cls.admin,
                    text=f'Тестовый пост{i}',
                    group=ContextTest.group_two)
                cls.posts.append(ContextTest.post)
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.admin)

    def test_group_list_belong_to_group(self):
        slug = self.group_one.slug
        response = self.guest_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': slug}))
        choice_group = response.context['page_obj'][0].group.title
        self.assertEqual(choice_group, 'Test group one')

    def test_posts_profile(self):
        response = self.guest_client.get(reverse(
            'posts:profile',
            kwargs={'username': self.user.username}))
        for i in range(len(response.context['page_obj'])):
            username = response.context['page_obj'][i].author.username
            self.assertEqual(username, 'Anonimus')

    def test_post_detail(self):
        response = self.guest_client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.id}))
        post = response.context['post'].id
        self.assertEqual(post, 12)
