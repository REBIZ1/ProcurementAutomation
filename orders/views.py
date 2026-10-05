from django.shortcuts import get_object_or_404
from django.db import transaction

from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.email import send_order_confirmation_email, send_order_invoice_email
from orders.models import Cart, CartItem, Contact, Order, OrderItem
from orders.serializers import (
    CartSerializer,
    CartItemCreateSerializer,
    ContactSerializer,
    OrderCreateSerializer,
    OrderSerializer,
    OrderListSerializer,
    OrderDetailSerializer,
    SupplierOrderSerializer,
    OrderStatusSerializer,
)
from products.models import ProductInfo, Shop


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


class ContactListCreateView(generics.ListCreateAPIView):
    """
    Получение и добавление контактов текущего пользователя
    """

    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Contact.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ContactDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Получение, изменение и удаление контакта текущего пользователя
    """

    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Contact.objects.filter(user=self.request.user)


class OrderCreateView(APIView):
    """
    Подтверждение заказа
    """

    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cart_id = serializer.validated_data["cart_id"]
        contact_id = serializer.validated_data["contact_id"]

        cart = get_object_or_404(
            Cart,
            pk=cart_id,
            user=request.user,
        )
        contact = get_object_or_404(
            Contact,
            pk=contact_id,
            user=request.user,
        )
        cart_items = CartItem.objects.select_related(
            "product_info",
            "product_info__product",
            "product_info__shop",
        ).filter(cart=cart)
        if not cart_items.exists():
            return Response(
                {"detail": "Корзина пуста."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        for cart_item in cart_items:
            product_info = cart_item.product_info
            if not product_info.shop.state:
                return Response(
                    {
                        "detail": (
                            f"Поставщик "
                            f"'{product_info.shop.name}' "
                            "временно не принимает заказы."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if product_info.quantity < cart_item.quantity:
                return Response(
                    {
                        "detail": (
                            f"Недостаточное количество товара "
                            f"'{product_info.product.name}'."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        order = Order.objects.create(
            user=request.user,
            contact=contact,
            status="new",
        )
        for cart_item in cart_items:
            product_info = cart_item.product_info
            OrderItem.objects.create(
                order=order,
                product_info=product_info,
                product_name=product_info.product.name,
                shop_name=product_info.shop.name,
                price=product_info.price,
                quantity=cart_item.quantity,
            )

            product_info.quantity -= cart_item.quantity
            product_info.save(update_fields=["quantity"])

        cart_items.delete()
        order = (
            Order.objects.select_related("contact", "user")
            .prefetch_related("items")
            .get(pk=order.pk)
        )
        send_order_confirmation_email(order)
        send_order_invoice_email(order)
        return Response(
            OrderSerializer(order).data,
            status=201,
        )


class OrderListView(generics.ListAPIView):
    """
    Получить список заказов текущего пользователя
    """

    serializer_class = OrderListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items")


class OrderDetailView(generics.RetrieveAPIView):
    """
    Получить детальную информацию о заказе
    """

    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Order.objects.filter(user=self.request.user)
            .select_related("contact")
            .prefetch_related("items")
        )


class SupplierOrderListView(generics.ListAPIView):
    """
    Представление для получения списка заказов поставщика
    """

    serializer_class = SupplierOrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.type != "shop":
            return Order.objects.none()
        shop = get_object_or_404(Shop, user=user)
        return (
            Order.objects.filter(items__product_info__shop=shop)
            .distinct()
            .prefetch_related("items")
        )


class SupplierOrderStatusView(APIView):
    """
    Представление для изменения статуса заказа поставщиком
    """

    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        if request.user.type != "shop":
            return Response(
                {"detail": "Только поставщик может изменять статус заказа."},
                status=status.HTTP_403_FORBIDDEN,
            )
        shop = get_object_or_404(
            Shop,
            user=request.user,
        )
        order = get_object_or_404(
            Order.objects.filter(items__product_info__shop=shop).distinct(),
            pk=pk,
        )
        serializer = OrderStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order.status = serializer.validated_data["status"]
        order.save(update_fields=["status", "updated_at"])
        order = Order.objects.prefetch_related("items").get(pk=order.pk)
        return Response(SupplierOrderSerializer(order).data)
