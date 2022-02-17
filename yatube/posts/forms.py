from django import forms

from posts.models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'group']
        labels = {
            'text': 'Текст поста',
            'group': 'Название сообщества'
        }
        help_texts = {
            'text': 'Введите текст поста',
            'group': 'Выбирите группу'
        }
