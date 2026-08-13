from django.contrib.auth.tokens import PasswordResetTokenGenerator


class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    """
    Генератор токенов для подтверждения email
    """

    pass


email_verification_token_generator = EmailVerificationTokenGenerator()


class PasswordResetTokenGeneratorCustom(PasswordResetTokenGenerator):
    """
    Генератор токенов для восстановления пароля
    """

    pass


password_reset_token_generator = PasswordResetTokenGeneratorCustom()
