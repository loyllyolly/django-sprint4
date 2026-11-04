"""Формы для приложения блога."""

from django import forms
from django.contrib.auth import get_user_model

from .models import Comment, Post

User = get_user_model()


class PostForm(forms.ModelForm):
    """Форма для создания и редактирования публикации."""

    class Meta:
        """Мета-параметры формы публикации."""

        model = Post
        exclude = ("author", "is_published")
        widgets = {
            "pub_date": forms.DateTimeInput(
                attrs={"type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
        }


class CommentForm(forms.ModelForm):
    """Форма для добавления и редактирования комментария."""

    class Meta:
        """Мета-параметры формы комментария."""

        model = Comment
        fields = ("text",)
        widgets = {
            "text": forms.Textarea(attrs={"rows": 3}),
        }


class ProfileEditForm(forms.ModelForm):
    """Форма для редактирования профиля пользователя."""

    class Meta:
        """Мета-параметры формы профиля."""

        model = User
        fields = ("first_name", "last_name", "username", "email")
