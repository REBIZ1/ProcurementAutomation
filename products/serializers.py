from rest_framework import serializers

from products.models import ProductParameter, ProductInfo, Product


class ProductParameterSerializer(serializers.ModelSerializer):
    """
    Сериализатор параметров товара
    """

    name = serializers.CharField(
        source="parameter.name",
        read_only=True,
    )

    class Meta:
        model = ProductParameter
        fields = (
            "name",
            "value",
        )


class ProductInfoSerializer(serializers.ModelSerializer):
    """
    Сериализатор информации о предложении товара в магазине
    """

    shop = serializers.CharField(
        source="shop.name",
        read_only=True,
    )
    parameters = ProductParameterSerializer(
        source="product_parameters",
        many=True,
        read_only=True,
    )

    class Meta:
        model = ProductInfo
        fields = (
            "id",
            "shop",
            "model",
            "price",
            "price_rrc",
            "quantity",
            "parameters",
        )


class ProductListSerializer(serializers.ModelSerializer):
    """
    Сериализатор товара для отображения в списке
    """

    category = serializers.CharField(
        source="category.name",
        read_only=True,
    )
    product_infos = ProductInfoSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "description",
            "category",
            "product_infos",
        )


class ProductDetailSerializer(serializers.ModelSerializer):
    """
    Сериализатор товара для детального отображения
    """

    category = serializers.CharField(
        source="category.name",
        read_only=True,
    )
    product_infos = ProductInfoSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "description",
            "category",
            "product_infos",
        )
