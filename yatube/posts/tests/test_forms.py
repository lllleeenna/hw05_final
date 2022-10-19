import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    """Тестирует форму создания и изменения поста."""

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

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group'
        )

    def setUp(self):
        self.client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_new_post(self):
        """При отправке валидной формы со страницы создания поста
        создается записи в БД."""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Пост в форме',
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), post_count + 1)

    def create_post_with_picture(self, client, group_id=None):
        """Создает пост с картинкой для тестов."""
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Пост в форме',
            'image': uploaded
        }
        if group_id:
            form_data['group'] = group_id

        client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

    def test_create_new_post_with_picture(self):
        """При создании поста с картинкой создается запись в БД."""
        post_count = Post.objects.count()
        self.create_post_with_picture(self.authorized_client)
        self.assertEqual(Post.objects.count(), post_count + 1)

    def test_create_new_post_with_picture_group(self):
        """При создании поста c группой и с картинкой создается запись в БД."""
        post_count = Post.objects.count()
        self.create_post_with_picture(
            self.authorized_client, self.group.id
        )
        self.assertEqual(Post.objects.count(), post_count + 1)

    def test_create_new_post_with_picture_unauthorized(self):
        """При создании поста с картинкой неавторизованным пользователем
        не создается запись в БД."""
        post_count = Post.objects.count()
        self.create_post_with_picture(self.client)
        self.assertEqual(Post.objects.count(), post_count)

    def test_create_new_post_with_picture_group_unauthorized(self):
        """При создании поста c группой и с картинкой не авторизованным
        пользователем не создается запись в БД."""
        post_count = Post.objects.count()
        self.create_post_with_picture(
            self.client, self.group.id
        )
        self.assertEqual(Post.objects.count(), post_count)

    def test_edit_post(self):
        """При отправке валидной формы со страницы редактирования поста
        происходит изменение в БД."""
        form_data = {
            'text': 'Новый тестовая запись',
        }
        self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        post = Post.objects.get(pk=1)
        self.assertEqual(post.text, form_data['text'])

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
