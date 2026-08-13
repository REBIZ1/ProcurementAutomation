from urllib.request import Request, urlopen
import yaml
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from products.services import import_products_from_yaml_content
from products.models import Shop


class ShopUpdatePriceView(APIView):
    """
    Обновление прайса поставщика
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.type != "shop":
            return Response(
                {
                    "Status": False,
                    "Error": "Только для поставщиков",
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        url = request.data.get("url")
        if not url:
            return Response(
                {
                    "Status": False,
                    "Error": "Не указан URL прайса",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        validate_url = URLValidator()
        try:
            validate_url(url)
        except ValidationError:
            return Response(
                {
                    "Status": False,
                    "Error": "Некорректный URL",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            request_object = Request(
                url,
                headers={
                    "User-Agent": "RetailPurchaseService/1.0",
                },
            )
            with urlopen(request_object, timeout=30) as response:
                content = response.read()
        except Exception as exc:
            return Response(
                {
                    "Status": False,
                    "Error": f"Не удалось загрузить прайс: {exc}",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            shop = import_products_from_yaml_content(
                content=content,
                user=request.user,
            )
        except (yaml.YAMLError, KeyError, ValueError) as exc:
            return Response(
                {
                    "Status": False,
                    "Error": f"Ошибка импорта: {exc}",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {
                "Status": True,
                "shop": shop.name,
            },
            status=status.HTTP_200_OK,
        )


class ShopStateView(APIView):
    """
    Включение или отключение приема заказов поставщиком
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.type != "shop":
            return Response(
                {
                    "Status": False,
                    "Error": "Только для поставщиков",
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        shop = get_object_or_404(Shop, user=request.user)
        state = request.data.get("state")
        if state is None:
            return Response(
                {
                    "Status": False,
                    "Error": "Необходимо указать state",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not isinstance(state, bool):
            return Response(
                {
                    "Status": False,
                    "Error": "Поле state должно иметь значение true или false",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        shop.state = state
        shop.save(update_fields=["state"])
        return Response(
            {
                "Status": True,
                "state": shop.state,
            },
            status=status.HTTP_200_OK,
        )
