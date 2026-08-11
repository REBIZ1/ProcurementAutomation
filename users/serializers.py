from django.contrib.auth import get_user_model
from rest_framework import serializers


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации новых пользователей
    """

    password = serializers.CharField(
        write_only=True,
        min_length=8,
    )
    password_confirm = serializers.CharField(
        write_only=True,
    )

    class Meta:
        model = User
        fields = (
            "email",
            "username",
            "first_name",
            "last_name",
            "company",
            "position",
            "password",
            "password_confirm",
        )

    def validate_email(self, value):
        """
        Проверяет уникальность email
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Пользователь с таким email уже существует"
            )
        return value

    def validate(self, attrs):
        """
        Проверяет совпадение пароля и подтверждения
        """
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Пароли не совпадают"}
            )
        return attrs

    def create(self, validated_data):
        """
        Создает нового пользователя с переданными данными
        """
        validated_data.pop("password_confirm")
        user = User.objects.create_user(
            password=validated_data.pop("password"),
            **validated_data,
        )
        return user
