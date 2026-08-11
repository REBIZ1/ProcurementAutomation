from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.conf import settings

from users.serializers import RegisterSerializer, LoginSerializer, UserSerializer
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


class LoginView(APIView):
    """
    Представление для авторизации
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token
        response = Response(
            {"detail": "Авторизация выполнена успешно."},
            status=status.HTTP_200_OK,
        )
        response.set_cookie(
            key="access_token",
            value=str(access),
            httponly=True,
            secure=settings.JWT_COOKIE_SECURE,
            samesite=settings.JWT_COOKIE_SAMESITE,
            max_age=30 * 60,
        )
        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            httponly=True,
            secure=settings.JWT_COOKIE_SECURE,
            samesite=settings.JWT_COOKIE_SAMESITE,
            max_age=7 * 24 * 60 * 60,
        )
        return response


class LogoutView(APIView):
    """
    Представление для logout
    """

    permission_classes = [AllowAny]

    def post(self, request):
        response = Response(
            {"detail": "Выход выполнен успешно."},
            status=status.HTTP_200_OK,
        )
        response.delete_cookie(
            "access_token",
            samesite=settings.JWT_COOKIE_SAMESITE,
        )
        response.delete_cookie(
            "refresh_token",
            samesite=settings.JWT_COOKIE_SAMESITE,
        )
        return response


class MeView(APIView):
    """
    Представление для получения текущего пользователя
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class RefreshView(APIView):
    """
    Представление для обновления access токена с использованием refresh токена
    """

    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return Response(
                {"detail": "Refresh token отсутствует"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        try:
            refresh = RefreshToken(refresh_token)
            access = refresh.access_token
            response = Response(
                {"detail": "Access token обновлен"},
                status=status.HTTP_200_OK,
            )
            response.set_cookie(
                key="access_token",
                value=str(access),
                httponly=True,
                secure=settings.JWT_COOKIE_SECURE,
                samesite=settings.JWT_COOKIE_SAMESITE,
                max_age=30 * 60,
            )
            return response
        except TokenError:
            return Response(
                {"detail": "Недействительный refresh token"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
