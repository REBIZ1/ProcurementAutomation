from rest_framework import serializers

from orders.models import CartItem, Cart


class CartItemSerializer(serializers.ModelSerializer):
    """
    Сериализатор позиции корзины
    """

    product = serializers.CharField(
        source="product_info.product.name",
        read_only=True,
    )
    shop = serializers.CharField(
        source="product_info.shop.name",
        read_only=True,
    )
    price = serializers.DecimalField(
        source="product_info.price",
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )
    total = serializers.DecimalField(
        source="total_price",
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = CartItem
        fields = (
            "id",
            "product",
            "shop",
            "price",
            "quantity",
            "total",
        )


class CartSerializer(serializers.ModelSerializer):
    """
    Сериализатор корзины пользователя
    """

    items = CartItemSerializer(
        many=True,
        read_only=True,
    )
    total_sum = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = Cart
        fields = (
            "id",
            "items",
            "total_sum",
        )


class CartItemCreateSerializer(serializers.Serializer):
    """
    Сериализатор для добавления товара в корзину
    """

    product_info_id = serializers.IntegerField(
        min_value=1,
    )
    quantity = serializers.IntegerField(
        min_value=1,
    )
