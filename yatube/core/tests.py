from django.test import Client, TestCase


class CoreURLTests(TestCase):
    """Тестирует URL приложиния core."""

    def setUp(self):
        self.guest_client = Client()

    def test_core_url404_uses_correct_template(self):
        """Проверка шаблона страницы 404."""

        response = self.guest_client.get('core.views.page_not_found')
        self.assertTemplateUsed(response, 'core/404.html')
