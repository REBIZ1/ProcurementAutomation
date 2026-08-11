from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError

from users.serializers import RegisterSerializer
from users.services import send_verification_email
from users.tokens import email_verification_token_generator

User = get_user_model()


class RegisterView(APIView):
    """
    Представление для регистрации новых пользователей
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Обрабатывает POST запрос на регистрацию пользователя
        """
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        send_verification_email(user)
        return Response(
            {
                "detail": (
                    "Регистрация прошла успешно. "
                    "На вашу почту отправлено письмо "
                    "для подтверждения email."
                )
            },
            status=status.HTTP_201_CREATED,
        )


class VerifyEmailView(APIView):
    """
    Представление для подтверждения email пользователя
    """
    permission_classes = [AllowAny]

    def get(self, request):
        """
        Обрабатывает GET запрос на подтверждение email
        """
        user_id = request.query_params.get("user_id")
        token = request.query_params.get("token")
        if not user_id or not token:
            raise ValidationError("Необходимо передать user_id и token")
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ValidationError("Пользователь не найден")
        if user.is_active:
            return Response(
                {"detail": "Email уже подтвержден"},
                status=status.HTTP_200_OK,
            )
        if not email_verification_token_generator.check_token(
            user,
            token,
        ):
            raise ValidationError("Недействительный или просроченный токен")
        user.is_active = True
        user.save(update_fields=["is_active"])
        return Response(
            {"detail": "Email успешно подтвержден."},
            status=status.HTTP_200_OK,
        )
