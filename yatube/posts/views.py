from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User
from .utils import get_page_paginator


def index(request):
    """функция для формирования главной страницы."""
    template = 'posts/index.html'
    posts = Post.objects.select_related('group')
    page_obj = get_page_paginator(request, posts)

    context = {
        'page_obj': page_obj,
    }

    return render(request, template, context)


def group_posts(request, slug):
    """функция для формирования страницы с записями сообщества."""
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts_group.all()
    page_obj = get_page_paginator(request, posts)

    context = {
        'group': group,
        'page_obj': page_obj
    }

    return render(request, template, context)


def profile(request, username):
    """Функция для формирования страницы профиля пользователя."""
    template = 'posts/profile.html'
    user = get_object_or_404(User, username=username)
    posts = user.posts.all()
    page_obj = get_page_paginator(request, posts)
    following = False

    if request.user.is_authenticated:
        if Follow.objects.filter(user=request.user, author=user).exists():
            following = True

    context = {
        'username': user,
        'page_obj': page_obj,
        'following': following
    }

    return render(request, template, context)


def post_detail(request, post_id):
    """Функция формирования страницы поста."""
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    count_posts = post.author.posts.count()
    comments = post.comments.all()
    form = CommentForm()

    context = {
        'post': post,
        'count_posts': count_posts,
        'comments': comments,
        'form': form
    }

    return render(request, template, context)


@login_required
def post_create(request):
    """Создание поста пользователем."""
    template = 'posts/create_post.html'
    form = PostForm(request.POST or None, files=request.FILES or None)

    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=request.user)

    context = {'form': form}

    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    """Изменение поста пользователем."""
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, pk=post_id)

    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)

    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post
    )

    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)

    context = {
        'is_edit': True,
        'form': form,
        'post_id': post_id
    }

    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    """Добавить комментарий к посту."""
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()

    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """Вывести посты авторов, на которых подписан пользователь."""
    template = 'posts/follow.html'
    posts = Post.objects.filter(author__following__user=request.user)
    page_obj = get_page_paginator(request, posts)
    context = {
        'page_obj': page_obj,
    }

    return render(request, template, context)


@login_required
def profile_follow(request, username):
    """Подписаться на автора."""
    author = get_object_or_404(User, username=username)
    if author == request.user:
        return redirect('posts:profile', username=username)
    if not Follow.objects.filter(user=request.user, author=author):
        Follow.objects.create(user=request.user, author=author)

    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    """Отписаться от автора."""
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('posts:profile', username=username)
