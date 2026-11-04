"""Представления для блога."""

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import CommentForm, PostForm, ProfileEditForm
from .models import Category, Comment, Post

User = get_user_model()
POSTS_PER_PAGE = 10


def get_published_posts():
    """Возвращает QuerySet опубликованных постов с аннотацией комментариев."""
    return (
        Post.objects.select_related("author", "category", "location")
        .filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True,
        )
        .annotate(comment_count=Count("comments"))
        .order_by("-pub_date")
    )


def paginate_queryset(request, queryset, per_page=POSTS_PER_PAGE):
    """Разбивает QuerySet на страницы."""
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)


def index(request):
    """Главная страница: список опубликованных постов с пагинацией."""
    posts = get_published_posts()
    page_obj = paginate_queryset(request, posts)
    return render(request, "blog/index.html", {"page_obj": page_obj})


def post_detail(request, post_id):
    """Страница отдельной публикации с комментариями и формой."""
    post = get_object_or_404(
        Post.objects.select_related("author", "category", "location"),
        pk=post_id,
    )
    if post.author != request.user:
        if (
            not post.is_published
            or (post.category and not post.category.is_published)
            or post.pub_date > timezone.now()
        ):
            raise Http404("Публикация не найдена")

    form = CommentForm()
    comments = post.comments.select_related("author").all()
    context = {
        "post": post,
        "form": form,
        "comments": comments,
    }
    return render(request, "blog/detail.html", context)


def category_posts(request, category_slug):
    """Страница категории со списком опубликованных постов."""
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True,
    )
    posts = (
        category.posts.select_related("author", "location", "category")
        .filter(
            is_published=True,
            pub_date__lte=timezone.now(),
        )
        .annotate(comment_count=Count("comments"))
        .order_by("-pub_date")
    )
    page_obj = paginate_queryset(request, posts)
    return render(
        request,
        "blog/category.html",
        {
            "category": category,
            "page_obj": page_obj,
        },
    )


def profile(request, username):
    """Страница пользователя с его публикациями."""
    profile_user = get_object_or_404(User, username=username)
    if request.user == profile_user:
        posts = (
            profile_user.posts.select_related(
                "author", "category", "location"
            )
            .annotate(comment_count=Count("comments"))
            .order_by("-pub_date")
        )
    else:
        posts = (
            profile_user.posts.select_related(
                "author", "category", "location"
            )
            .filter(
                is_published=True,
                category__is_published=True,
                pub_date__lte=timezone.now(),
            )
            .annotate(comment_count=Count("comments"))
            .order_by("-pub_date")
        )
    page_obj = paginate_queryset(request, posts)
    context = {
        "profile": profile_user,
        "page_obj": page_obj,
    }
    return render(request, "blog/profile.html", context)


@login_required
def edit_profile(request):
    """Редактирование профиля пользователя."""
    form = ProfileEditForm(request.POST or None, instance=request.user)
    if form.is_valid():
        form.save()
        return redirect("blog:profile", username=request.user.username)
    return render(request, "blog/user.html", {"form": form})


@login_required
def post_create(request):
    """Создание новой публикации."""
    form = PostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect("blog:profile", username=request.user.username)
    return render(request, "blog/create.html", {"form": form})


@login_required
def post_edit(request, post_id):
    """Редактирование публикации автором."""
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect("blog:post_detail", post_id=post_id)
    form = PostForm(request.POST or None, request.FILES or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect("blog:post_detail", post_id=post_id)
    return render(request, "blog/create.html", {"form": form})


@login_required
def post_delete(request, post_id):
    """Удаление публикации автором."""
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect("blog:post_detail", post_id=post_id)
    if request.method == "POST":
        post.delete()
        return redirect("blog:index")
    form = PostForm(instance=post)
    return render(request, "blog/create.html", {"form": form})


@login_required
def add_comment(request, post_id):
    """Добавление комментария к публикации."""
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
    return redirect("blog:post_detail", post_id=post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    """Редактирование комментария автором."""
    comment = get_object_or_404(Comment, pk=comment_id, post_id=post_id)
    if comment.author != request.user:
        return redirect("blog:post_detail", post_id=post_id)
    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        return redirect("blog:post_detail", post_id=post_id)
    return render(
        request,
        "blog/comment.html",
        {"form": form, "comment": comment},
    )


@login_required
def delete_comment(request, post_id, comment_id):
    """Удаление комментария автором."""
    comment = get_object_or_404(Comment, pk=comment_id, post_id=post_id)
    if comment.author != request.user:
        return redirect("blog:post_detail", post_id=post_id)
    if request.method == "POST":
        comment.delete()
        return redirect("blog:post_detail", post_id=post_id)
    base_form = forms.Form()
    return render(
        request,
        "blog/comment.html",
        {"comment": comment, "form": base_form},
    )
