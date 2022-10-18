from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse


class StaticURLTests(TestCase):
    """Тестирует доступность страниц и названия шаблонов приложине."""

    URL_TEMPLATES_NAMES = {
        '/about/author/': 'about/author.html',
        '/about/tech/': 'about/tech.html',
    }

    def setUp(self):
        self.guest_client = Client()

    def test_about_url_exists_at_desired_location(self):
        """Проверка доступности url адресов приложения about."""
        for url in StaticURLTests.URL_TEMPLATES_NAMES.keys():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_url_uses_correct_template(self):
        """Проверка шаблонов для приложения about."""
        for url, template in StaticURLTests.URL_TEMPLATES_NAMES.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)


class StaticViewsTests(TestCase):

    """Проверяет соответствие шаблонов именам, доступность URL по имени."""
    def setUp(self):
        self.guest_client = Client()

    def test_page_accessible_by_name(self):
        """URL генерируемый при помощи имени доступен"""
        reverse_name = [reverse('about:author'), reverse('about:tech')]
        for name in reverse_name:
            with self.subTest(name=name):
                response = self.guest_client.get(name)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_page_uses_correct_template(self):
        """Странице сгенерированной при помощи имени соответствует шаблон"""
        names_templates_pages = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
        }
        for reverse_name, template in names_templates_pages.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
