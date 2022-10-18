from http import HTTPStatus

from django.test import Client, TestCase
from posts.models import User


class UsersURLTests(TestCase):
    """Тестирует доступность страниц и названия шаблонов приложине."""
    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.user = User.objects.create_user(username='Elena')
        self.authorized_client.force_login(self.user)

    def test_users_page_url_exists_unauthorized(self):
        """Тестирование общедоступных страниц."""
        pages = [
            '/auth/login/', '/auth/signup/',
            '/auth/password_reset/', '/auth/password_reset/done/',
            '/auth/reset/<uidb64>/<token>/', '/auth/reset/done/',
        ]
        for page in pages:
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_users_page_url_exists_authorized(self):
        """Тестирование страниц доступных авторизованному пользователю."""
        pages = [
            '/auth/password_change/', '/auth/password_change/done/',
            '/auth/logout/'
        ]
        for page in pages:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        url_templates_names = {
            '/auth/signup/': 'users/signup.html',
            '/auth/login/': 'users/login.html',
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/password_change/done/': 'users/password_change_done.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/reset/<uidb64>/<token>/': (
                'users/password_reset_confirm.html'
            ),
            '/auth/reset/done/': 'users/password_reset_complete.html',
            '/auth/logout/': 'users/logged_out.html',
        }
        for url, template in url_templates_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
