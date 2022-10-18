from django.test import Client, TestCase
from django.urls import reverse
from posts.models import User


class UserFormTests(TestCase):
    """Тестирует форму создания пользователя."""

    def setUp(self):
        self.client = Client()

    def test_create_new_post(self):
        """При отправке валидной формы со страницы создания пользователя
        создается записи в БД."""
        user_count = User.objects.count()
        form_data = {
            'username': 'Elena',
            'password1': 'Elena123456',
            'password2': 'Elena123456'
        }
        self.client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertEqual(User.objects.count(), user_count + 1)
