from django.core.paginator import Paginator

NUMBER_POSTS = 10


def get_page_paginator(request, posts):
    paginator = Paginator(posts, NUMBER_POSTS)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
