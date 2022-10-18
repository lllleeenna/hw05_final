import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import models
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Comment, Group, Post, Follow

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    """Тестирует использование во view-функциях правильных html-шаблонов.
    Проверка, соответствует ли ожиданиям словарь context, предаваемый
    в шаблон при вызове."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='Elena'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='testovaya-gruppa',
            description='Тестовое описание',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='Какая-то тестовая запись',
            author=cls.user,
            group=cls.group,
            image=cls.uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostPagesTests.user)

    def post_test_context(self, first_object):
        """Проверяет содержимое поста, переданное в шаблон.
        Принимает объект поста, и сравнивает его с тестовой записью."""
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        post_group_0 = first_object.group
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, 'Какая-то тестовая запись')
        self.assertEqual(post_author_0, PostPagesTests.user)
        self.assertEqual(post_group_0, PostPagesTests.group)
        self.assertTrue(post_image_0)
        self.assertIsInstance(post_image_0, models.fields.files.ImageFieldFile)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон в приложении posts."""
        names_templates_pages = {
            reverse('posts:posts_list'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': 'testovaya-gruppa'}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': 'Elena'}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': '1'}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': '1'}
            ): 'posts/create_post.html'
        }

        for reverse_name, template in names_templates_pages.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_posts_list_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:posts_list'))
        first_object = response.context['page_obj'][0]
        self.post_test_context(first_object)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'testovaya-gruppa'})
        )
        first_object = response.context['page_obj'][0]
        self.post_test_context(first_object)
        self.assertEqual(response.context.get('group'), PostPagesTests.group)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'Elena'})
        )
        first_object = response.context['page_obj'][0]
        self.post_test_context(first_object)
        self.assertEqual(response.context.get('username'), PostPagesTests.user)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': '1'})
        )
        post_object = response.context.get('post')
        self.post_test_context(post_object)
        self.assertEqual(response.context.get('count_posts'), 1)

    def test_create_post_page_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_post_page_show_correct_context(self):
        """Шаблон create_post для изменения поста сформирован с правильным
        контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': 1})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        self.assertTrue(response.context.get('is_edit'))
        self.assertEqual(response.context.get('post_id'), 1)


class PaginatorViewsTest(TestCase):
    """Проверяет работу Paginator на главной странице, странице группы
    и в профайле пользователя."""

    pages = [
        reverse('posts:posts_list'),
        reverse('posts:group_list', kwargs={'slug': 'testovaya-gruppa'}),
        reverse('posts:profile', kwargs={'username': 'Elena'})
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='Elena'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='testovaya-gruppa',
            description='Тестовое описание',
        )
        for i in range(13):
            Post.objects.create(
                text='Какая-то тестовая запись' + str(i),
                author=cls.user,
                group=cls.group
            )

    def setUp(self):
        self.client = Client()

    def test_first_page_contains_ten_records(self):
        for page in PaginatorViewsTest.pages:
            with self.subTest(page=page):
                response = self.client.get(page)
                self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        for page in PaginatorViewsTest.pages:
            with self.subTest(page=page):
                response = self.client.get(page + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 3)


class PostInGroupTest(TestCase):
    """Тестирует создание поста с указанием группы.
    Проверяет наличие поста на главной странице, странице группы
    и в профайле пользователя."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='Elena'
        )
        cls.group1 = Group.objects.create(
            title='Тестовая группа 1',
            slug='testovaya-gruppa-1',
            description='Тестовое описание 1',
        )
        cls.group2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='testovaya-gruppa-2',
            description='Тестовое описание 2',
        )
        cls.post = Post.objects.create(
            text='Какая-то тестовая запись',
            author=cls.user,
            group=cls.group1
        )

    def setUp(self):
        self.client = Client()

    def test_post_on_page(self):
        """Проверяет, появился ли пост, в котором указана группа,
        на главной странице, странице группы и в профайле пользователя."""
        pages = [
            reverse('posts:posts_list'),
            reverse('posts:group_list', kwargs={'slug': 'testovaya-gruppa-1'}),
            reverse('posts:profile', kwargs={'username': 'Elena'})
        ]
        for page in pages:
            with self.subTest(page=page):
                response = self.client.get(page)
                post_object = response.context['page_obj'][0]
                self.assertEqual(post_object.text, 'Какая-то тестовая запись')

    def test_post_is_not_on_page_another_group(self):
        """Проверяет отсутствие поста на странице другой группы."""
        response = self.client.get(
            reverse('posts:group_list', kwargs={'slug': 'testovaya-gruppa-2'})
        )
        self.assertEqual(len(response.context['page_obj']), 0)


class CommentsTests(TestCase):
    """Тестирует создание комментария к постау."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='Elena'
        )

        cls.post = Post.objects.create(
            text='Какая-то тестовая запись',
            author=cls.user,
        )

        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Комментарий к посту'
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(CommentsTests.user)

    def test_comment_on_page_post(self):
        """После успешной отправки комментарий появляется на странице поста."""
        response = self.client.get(
            reverse('posts:post_detail', kwargs={'post_id': 1})
        )
        comment = response.context['comments'][0]
        self.assertEqual(comment.text, 'Комментарий к посту')


class CacheTests(TestCase):
    """Тестирование кэша страниц."""

    def setUp(self):
        self.user = User.objects.create(
            username='Elena'
        )
        Post.objects.create(
            text='Тестовая запись для проверки кэша',
            author=self.user
        )
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_cache_posts_list(self):
        """Кэширование главной страницы."""
        cache.clear()
        response = self.client.get(reverse('posts:posts_list'))
        self.assertIn(
            'Тестовая запись для проверки кэша', response.content.decode(
                'UTF-8'
            )
        )
        self.assertEqual(Post.objects.count(), 1)
        Post.objects.all().delete()
        self.assertEqual(Post.objects.count(), 0)
        self.assertIn(
            'Тестовая запись для проверки кэша', response.content.decode(
                'UTF-8'
            )
        )


class FollowTests(TestCase):
    """Тестирует систему подписок на авторов."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_auth = User.objects.create(
            username='auth'
        )
        cls.user_follow = User.objects.create(
            username='user_follow'
        )
        cls.user_unfollow = User.objects.create(
            username='user_unfollow'
        )
        Follow.objects.create(
            user=cls.user_follow,
            author=cls.user_auth
        )

    def setUp(self):
        self.client_follow = Client()
        self.client_follow.force_login(FollowTests.user_follow)
        self.client_unfollow = Client()
        self.client_unfollow.force_login(FollowTests.user_unfollow)

    def test_create_post_follow(self):
        """Новая запись пользователя появляется в ленте тех,
        кто на него подписан и не появляется в ленте тех, кто не подписан."""
        response_follow = self.client_follow.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(len(response_follow.context['page_obj']), 0)

        response_unfollow = self.client_unfollow.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(len(response_unfollow.context['page_obj']), 0)

        Post.objects.create(
            author=FollowTests.user_auth,
            text='Тестовая запись для проверки подписок'
        )

        response_follow = self.client_follow.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(len(response_follow.context['page_obj']), 1)

        post_object = response_follow.context['page_obj'][0]
        self.assertEqual(
            post_object.text, 'Тестовая запись для проверки подписок'
        )

        response_unfollow = self.client_unfollow.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(len(response_unfollow.context['page_obj']), 0)
