from rest_framework import serializers

from orders.models import CartItem, Cart, Contact


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


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = (
            "id",
            "last_name",
            "first_name",
            "patronymic",
            "email",
            "phone",
            "city",
            "street",
            "house",
            "building",
            "structure",
            "apartment",
        )
        read_only_fields = ("id",)

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)
