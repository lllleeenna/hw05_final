from django.contrib import admin

from .models import Comment, Follow, Group, Post


class PostAdmin(admin.ModelAdmin):
    """Класс для работы со статьями в админ-панели."""

    list_display = ('pk', 'text', 'image', 'pub_date', 'author', 'group')
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'
    list_editable = ('group',)


class GroupAdmin(admin.ModelAdmin):
    """Класс для работы с сообществами в админ-панели."""

    list_display = ('title', 'slug', 'description')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}


class FollowAdmin(admin.ModelAdmin):
    """Класс для работы с подписками в админ-панели."""

    list_display = ('user', 'author')
    raw_id_fields = ('user', 'author')


class CommentAdmin(admin.ModelAdmin):
    """Класс для работы с комментариями в админ-панели."""

    list_display = ('author', 'text')
    search_fields = ('text',)


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(Comment, CommentAdmin)
