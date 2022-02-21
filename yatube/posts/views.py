from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from posts.forms import PostForm
from .models import Post, Group, User


POSTS_PER_PAGE = 10


def get_paginator(request, page, num):
    paginator = Paginator(page, num)
    page_numder = request.GET.get('page')
    page_obj: Paginator = paginator.get_page(page_numder)
    return page_obj


def index(request):
    template = 'posts/index.html'
    title = 'Последние обновления на сайте'
    posts = Post.objects.all()
    page_obj = get_paginator(request, posts, POSTS_PER_PAGE)
    context = {
        'posts': posts,
        'page_obj': page_obj,
        'title': title}
    return render(request, template, context)


def group_post(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.groups.all()
    description = group.description
    page_obj = get_paginator(request, posts, POSTS_PER_PAGE)
    title = f'Вы в сообществе {group}'
    context = {
        'description': description,
        'page_obj': page_obj,
        'group': group,
        'title': title}
    return render(request, template, context)


def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = user.posts.all()
    count = posts.count()
    page_obj = get_paginator(request, posts, POSTS_PER_PAGE)
    context = {
        'count': count,
        'page_obj': page_obj,
        'author': user
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    author_posts = post.author.posts.all()
    author_name = post.author
    user = request.user
    count = author_posts.count()
    context = {
        'author_name': author_name,
        'user': user,
        'count': count,
        'post': post
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    user = request.user
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = user
        post.save()
        return redirect('posts:profile', username=user.username)
    form = PostForm()
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    return render(request, 'posts/create_post.html',
                  {'form': form, 'post_id': post_id, 'is_edit': True})
