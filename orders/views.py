from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models import Cart, CartItem
from orders.serializers import CartSerializer, CartItemCreateSerializer
from products.models import ProductInfo


class CartView(APIView):
    """
    Получение корзины текущего пользователя
    """

    permission_classes = [IsAuthenticated]

    def get_cart(self, user):
        cart, _ = Cart.objects.get_or_create(user=user)
        return cart

    def get(self, request):
        cart = self.get_cart(request.user)
        cart = Cart.objects.prefetch_related(
            "items__product_info__product",
            "items__product_info__shop",
        ).get(pk=cart.pk)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def post(self, request):
        serializer = CartItemCreateSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        product_info_id = serializer.validated_data["product_info_id"]
        quantity = serializer.validated_data["quantity"]
        product_info = get_object_or_404(
            ProductInfo,
            pk=product_info_id,
        )
        if product_info.quantity < quantity:
            return Response(
                {"detail": ("Недостаточное количество товара на складе")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cart = self.get_cart(request.user)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product_info=product_info,
            defaults={
                "quantity": quantity,
            },
        )
        if not created:
            new_quantity = cart_item.quantity + quantity
            if product_info.quantity < new_quantity:
                return Response(
                    {"detail": ("Недостаточное количество товара на складе")},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            cart_item.quantity = new_quantity
            cart_item.save(
                update_fields=["quantity"],
            )
        return Response(
            CartSerializer(cart).data,
            status=status.HTTP_201_CREATED,
        )


class CartItemDeleteView(APIView):
    """
    Удаление товара из корзины
    """

    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        cart = get_object_or_404(
            Cart,
            user=request.user,
        )
        cart_item = get_object_or_404(
            CartItem,
            cart=cart,
            pk=pk,
        )
        cart_item.delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )
