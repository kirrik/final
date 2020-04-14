from django.forms import ModelForm
from .models import Post, Group, Comment

class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('group', 'text', 'image')
        labels = { 'text': 'Текст вашего поста:', 'group': 'Группа:', 'image': 'Изображение:'}

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {'text': 'Ваш комментарий'}
