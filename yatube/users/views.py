from django.contrib.auth.views import (
    PasswordChangeDoneView,
    PasswordChangeView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView
)
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CreationForm


class SignUp(CreateView):
    """Регистрация пользователя."""

    form_class = CreationForm
    success_url = reverse_lazy('posts:posts_list')
    template_name = 'users/signup.html'


class PasswordChange(PasswordChangeView):
    """Задать новый пароль."""

    success_url = reverse_lazy('users:password_change_done')


class PasswordChangeDone(PasswordChangeDoneView):
    """Пароль успешно изменен."""

    template_name = 'users/password_change_done.html'


class PasswordReset(PasswordResetView):
    """Инициирует процедуру сброса пароля."""

    template_name = 'users/password_reset_form.html'
    subject_template_name = 'email/reset_letter_subject.txt'
    email_template_name = 'email/reset_letter_body.txt'
    success_url = reverse_lazy('users:password_reset_done')


class PasswordResetDone(PasswordResetDoneView):
    """Сообщение отправлено на почту."""

    template_name = 'users/password_reset_done.html'


class PasswordResetConfirm(PasswordResetConfirmView):
    """Выполняет сброс пароля."""

    success_url = reverse_lazy('users:password_reset_complete')


class PasswordResetComplete(PasswordResetCompleteView):
    """Пароль успешно сброшен."""

    template_name = 'users/password_reset_complete.html'
