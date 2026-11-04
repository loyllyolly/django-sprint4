"""Модели для приложения блога."""

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class PublishedModel(models.Model):
    """Абстрактная модель с флагом публикации и датой создания."""

    is_published = models.BooleanField(
        default=True,
        verbose_name="Опубликовано",
        help_text="Снимите галочку, чтобы скрыть публикацию.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Добавлено",
    )

    class Meta:
        """Мета-параметры модели."""

        abstract = True


BaseModel = PublishedModel


class Category(PublishedModel):
    """Тематическая категория."""

    title = models.CharField(
        max_length=256,
        verbose_name="Заголовок",
    )
    description = models.TextField(
        verbose_name="Описание",
    )
    slug = models.SlugField(
        unique=True,
        verbose_name="Идентификатор",
        help_text=(
            "Идентификатор страницы для URL; "
            "разрешены символы латиницы, цифры, дефис и подчёркивание."
        ),
    )

    class Meta:
        """Мета-параметры модели."""

        verbose_name = "категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        """Строковое представление категории."""
        return self.title


class Location(PublishedModel):
    """Географическая метка."""

    name = models.CharField(
        max_length=256,
        verbose_name="Название места",
    )

    class Meta:
        """Мета-параметры модели."""

        verbose_name = "местоположение"
        verbose_name_plural = "Местоположения"

    def __str__(self):
        """Строковое представление локации."""
        return self.name


class Post(PublishedModel):
    """Публикация."""

    title = models.CharField(
        max_length=256,
        verbose_name="Заголовок",
    )
    text = models.TextField(
        verbose_name="Текст",
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата и время публикации",
        help_text=(
            "Если установить дату и время в будущем — "
            "можно делать отложенные публикации."
        ),
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор публикации",
        related_name="posts",
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Местоположение",
        related_name="posts",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Категория",
        related_name="posts",
    )
    image = models.ImageField(
        upload_to="posts_images",
        blank=True,
        verbose_name="Изображение",
    )

    class Meta:
        """Мета-параметры модели."""

        verbose_name = "публикация"
        verbose_name_plural = "Публикации"
        ordering = ("-pub_date",)

    def __str__(self):
        """Строковое представление публикации."""
        return self.title


class Comment(models.Model):
    """Комментарий к публикации."""

    text = models.TextField(
        verbose_name="Текст комментария",
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Публикация",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Автор комментария",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Добавлено",
    )

    class Meta:
        """Мета-параметры комментария."""

        verbose_name = "комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ("created_at",)

    def __str__(self):
        """Строковое представление комментария."""
        return self.text[:20]
