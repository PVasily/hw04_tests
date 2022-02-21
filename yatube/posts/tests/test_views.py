from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django import forms

from ..models import Post, Group
from ..forms import PostForm


User = get_user_model()


class PostTemplatesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='auth')
        cls.form = PostForm
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Test group',
            slug='test-slug',
            description='Test description'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )

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
        form_context = response.context.get('form')
        self.assertTrue(form_context)
        self.assertIsInstance(form_context, self.form)
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_types_fields_forms_post_edit(self):
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': 1}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        is_edit = response.context.get('is_edit')
        form_context = response.context.get('form')
        self.assertTrue(is_edit)
        self.assertEqual(type(is_edit), bool)
        self.assertIsNotNone(form_context)
        self.assertIsInstance(form_context, self.form)
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

    def test_group_list_belong_to_group(self):
        slug = self.group.slug
        response = self.guest_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': slug}))
        choice_group = response.context['page_obj'][0].group.title
        self.assertEqual(choice_group, 'Test group')

    def test_posts_profile(self):
        response = self.guest_client.get(reverse(
            'posts:profile',
            kwargs={'username': self.user.username}))
        for i in range(len(response.context['page_obj'])):
            username = response.context['page_obj'][i].author.username
            self.assertEqual(username, 'auth')

    def test_post_detail(self):
        response = self.guest_client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.id}))
        post = response.context['post'].id
        self.assertEqual(post, 1)


class PaginatorTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='Anonimus')
        cls.guest_client = Client()
        cls.group = Group.objects.create(
            title='Test group',
            slug='test-slug',
            description='Test description')
        BATCH_SIZE = 13
        cls.list_posts = [Post(
            text=f'Тестовый пост {i}',
            author=cls.user,
            group=cls.group) for i in range(BATCH_SIZE)]
        cls.posts = Post.objects.bulk_create(cls.list_posts, BATCH_SIZE)

    def test_paginator(self):
        slug = self.group.slug
        username = self.user.username
        num_page = {'page': 2}
        qnt_per_first_page = 10
        qnt_per_last_page = 3
        tup_addr = (
            ('/', '', qnt_per_first_page),
            (f'/group/{slug}/', '', qnt_per_first_page),
            (f'/profile/{username}/', '', qnt_per_first_page),
            ('/', num_page, qnt_per_last_page),
            (f'/profile/{username}/', num_page, qnt_per_last_page),
            (f'/group/{slug}/', num_page, qnt_per_last_page)
        )
        for address, num, qnt in tup_addr:
            with self.subTest(address=address):
                response = self.guest_client.get(address, num)
                len_page = len(response.context['page_obj'])
                self.assertEqual(len_page, qnt)
