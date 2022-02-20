from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост, созданный для тестирования',
        )

    def test_model_post_have_correct_object_names(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        method_str = self.post.__str__()
        self.assertEqual(method_str, self.post.text[:15])

    def test_model_group_have_correct_object_names(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        result = self.group.title
        method_str = self.group.__str__()
        self.assertEqual(method_str, result)

    def test_models_fields(self):
        """Проверяем verbose_name и help_text у моделей."""
        post_field = self.post._meta.get_field
        group_field = self.group._meta.get_field
        dict_match = {
            f"{post_field('text').help_text}": 'Введите текст',
            f"{post_field('text').verbose_name}": 'Текст поста',
            f"{post_field('pub_date').verbose_name}": 'Дата создания',
            f"{post_field('group').help_text}": 'Выбирите название группы',
            f"{post_field('group').verbose_name}": 'Группа',
            f"{post_field('author').verbose_name}": 'Автор',
            f"{group_field('title').verbose_name}": 'Группа',
            f"{group_field('description').verbose_name}": 'Описание группы'
        }
        for field, value in dict_match.items():
            self.assertEqual(field, value)
