from http import HTTPStatus

from django.test import Client, TestCase

from ..models import Group, Post, User


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_homepage(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)


class PostsURLTests(TestCase):
    """Тестирует доступность страниц и названия шаблонов приложине."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='auth'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='testovaya-gruppa',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Какая-то тестовая запись',
            author=cls.user,
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.user = User.objects.create_user(username='Elena')
        self.authorized_client.force_login(self.user)
        self.authorized_author_client = Client()
        self.authorized_author_client.force_login(PostsURLTests.user)

    def test_post_page_url_exists_unauthorized(self):
        """Тестирование общедоступных страниц."""
        pages = [
            '/', '/group/testovaya-gruppa/', '/profile/auth/', '/posts/1/'
        ]
        for page in pages:
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_unexisting_page_url_unauthorized(self):
        """Тестирование несуществующей страницы."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_post_create_url_exists_authorized(self):
        """Тестирование создания поста авторизованым пользователем."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_url_exists_author(self):
        """Тестирование изменения поста автором."""
        response = self.authorized_author_client.get('/posts/1/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_create_url_redirect_unauthorized_on_login(self):
        """Страница /create/ перенаправит неавторизованного пользователя
        на страницу логина.
        """
        response = self.guest_client.get('/create/')
        self.assertRedirects(
            response, '/auth/login/?next=/create/'
        )

    def test_post_edit_url_redirect_unauthorized_on_login(self):
        """Страница /posts/<post_id>/edit/ перенаправит неавторизованного
        пользователя на страницу логина.
        """
        response = self.guest_client.get('/posts/1/edit/')
        self.assertRedirects(
            response, '/auth/login/?next=/posts/1/edit/'
        )

    def test_post_edit_url_redirect_authorized_on_detail(self):
        """Страница /posts/<post_id>/edit/ перенаправит авторизованного
        пользователя, не являющегося автором поста,
        на страницу просмотра поста.
        """
        response = self.authorized_client.get('/posts/1/edit/')
        self.assertRedirects(
            response, '/posts/1/'
        )

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        url_templates_names = {
            '/': 'posts/index.html',
            '/group/testovaya-gruppa/': 'posts/group_list.html',
            '/profile/auth/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/posts/1/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
            '/follow/': 'posts/follow.html',
        }
        for url, template in url_templates_names.items():
            with self.subTest(url=url):
                response = self.authorized_author_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_comment_url_redirect_authorized_on_post_detail(self):
        """При создании комментария авторизованного пользователя перенаправляет
        на страницу поста."""
        response = self.authorized_client.get('/posts/1/comment/')
        self.assertRedirects(
            response, '/posts/1/'
        )

    def test_comment_url_redirect_unauthorized_on_login(self):
        """Страница posts/<int:post_id>/comment/ перенаправит неавторизованного
        пользователя на страницу логина.
        """
        response = self.guest_client.get('/posts/1/comment/')
        self.assertRedirects(
            response, '/auth/login/?next=/posts/1/comment/'
        )

    def test_follow_url_exists_authorized(self):
        """Авторизованный пользователь может подписываться
        на других пользователей."""
        response = self.authorized_client.get('/profile/auth/follow/')
        self.assertRedirects(response, '/profile/auth/')

    def test_unfollow_url_exists_authorized(self):
        """Авторизованный пользователь может отписаться
        от других пользователей."""
        response = self.authorized_client.get('/profile/auth/unfollow/')
        self.assertRedirects(response, '/profile/auth/')

    def test_follow_url_unauthorized(self):
        """Неавторизованного пользователя перенаправит на страницу логина."""
        response = self.guest_client.get('/profile/auth/follow/')
        self.assertRedirects(
            response, '/auth/login/?next=/profile/auth/follow/'
        )

    def test_unfollow_url_unauthorized(self):
        """Неавторизованного пользователя перенаправит на страницу логина."""
        response = self.guest_client.get('/profile/auth/unfollow/')
        self.assertRedirects(
            response, '/auth/login/?next=/profile/auth/unfollow/'
        )
