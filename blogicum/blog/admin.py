"""Админ-зона для приложения блога."""

from django.contrib import admin

from .models import Category, Comment, Location, Post

admin.site.empty_value_display = "Не задано"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Админ-зона для категорий."""

    list_display = (
        "title",
        "slug",
        "is_published",
        "created_at",
    )
    list_editable = ("is_published",)
    search_fields = ("title", "slug")


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    """Админ-зона для локаций."""

    list_display = (
        "name",
        "is_published",
        "created_at",
    )
    list_editable = ("is_published",)
    search_fields = ("name",)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Админ-зона для публикаций."""

    list_display = (
        "title",
        "pub_date",
        "author",
        "category",
        "location",
        "is_published",
        "created_at",
    )
    list_editable = ("is_published",)
    list_filter = ("is_published", "category", "location")
    search_fields = ("title", "text")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Админ-зона для комментариев."""

    list_display = ("text", "post", "author", "created_at")
    search_fields = ("text", "author__username")
