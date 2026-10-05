from django.urls import reverse
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

from users.tokens import (
    email_verification_token_generator,
    password_reset_token_generator,
)


def send_verification_email(request, user):
    """
    Отправляет письмо для подтверждения email пользователя
    """
    token = email_verification_token_generator.make_token(user)
    verification_url = request.build_absolute_uri(
        f"{reverse('verify-email')}?user_id={user.id}&token={token}"
    )
    subject = "Подтверждение регистрации"
    text_message = f"""
Здравствуйте, {user.username}!
Спасибо за регистрацию.
Для подтверждения email перейдите по ссылке:
{verification_url}
""".strip()

    html_message = f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>{subject}</title>
</head>
<body>
    <h2>Здравствуйте, {user.username}!</h2>
    
    <p>Спасибо за регистрацию.</p>
    <p>
        Для подтверждения email перейдите по ссылке:
    </p>
    <p>
        <a href="{verification_url}">
            Подтвердить email
        </a>
    </p>
</body>
</html>
"""
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    email.attach_alternative(
        html_message,
        "text/html",
    )
    email.send()


def send_password_reset_email(request, user):
    """
    Отправляет письмо для восстановления пароля
    """

    token = password_reset_token_generator.make_token(user)
    reset_url = request.build_absolute_uri(
        f"{reverse('password-reset-confirm')}?user_id={user.id}&token={token}"
    )
    subject = "Восстановление пароля"
    text_message = f"""
Здравствуйте, {user.username}!
Вы запросили восстановление пароля.
Для установки нового пароля перейдите по ссылке:
{reset_url}
""".strip()

    html_message = f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>{subject}</title>
</head>
<body>
    <h2>Здравствуйте, {user.username}!</h2>
    <p>
        Вы запросили восстановление пароля.
    </p>
    <p>
        Для установки нового пароля перейдите по ссылке:
    </p>
    <p>
        <a href="{reset_url}">
            Восстановить пароль
        </a>
    </p>
</body>
</html>
"""
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    email.attach_alternative(
        html_message,
        "text/html",
    )
    email.send()
