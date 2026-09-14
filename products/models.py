from django.conf import settings
from django.db import models


class Shop(models.Model):
    """
    Поставщик товаров
    """

    name = models.CharField(
        max_length=100,
        verbose_name="Название",
    )
    url = models.URLField(
        verbose_name="Ссылка на сайт",
        blank=True,
        null=True,
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="shop",
        verbose_name="Пользователь",
        blank=True,
        null=True,
    )
    state = models.BooleanField(
        default=True,
        verbose_name="Принимает заказы",
    )

    class Meta:
        verbose_name = "Поставщик"
        verbose_name_plural = "Поставщики"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Category(models.Model):
    """
    Категория товара
    """

    name = models.CharField(
        max_length=100,
        verbose_name="Название",
    )
    shops = models.ManyToManyField(
        Shop,
        related_name="categories",
        verbose_name="Поставщики",
        blank=True,
    )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Основная сущность товара
    """

    name = models.CharField(
        max_length=255,
        verbose_name="Название",
    )
    description = models.TextField(
        blank=True,
        default="",
        verbose_name="Описание",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name="Категория",
    )

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ("name",)

    def __str__(self):
        return self.name


class ProductInfo(models.Model):
    """
    Информация о конкретном товаре у конкретного поставщика
    """

    model = models.CharField(
        max_length=255,
        verbose_name="Модель",
        blank=True,
    )
    external_id = models.PositiveIntegerField(
        verbose_name="Внешний ID",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="product_infos",
        verbose_name="Товар",
    )
    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name="product_infos",
        verbose_name="Поставщик",
    )
    quantity = models.PositiveIntegerField(
        verbose_name="Количество",
        default=0,
    )
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Цена",
    )
    price_rrc = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Рекомендуемая розничная цена",
    )

    class Meta:
        verbose_name = "Информация о товаре"
        verbose_name_plural = "Информация о товарах"
        constraints = [
            models.UniqueConstraint(
                fields=["product", "shop", "external_id"],
                name="unique_product_info",
            ),
        ]

    def __str__(self):
        return f"{self.product.name} — {self.shop.name}"


class Parameter(models.Model):
    """
    Характеристика товара
    """

    name = models.CharField(
        max_length=100,
        verbose_name="Название",
    )

    class Meta:
        verbose_name = "Характеристика"
        verbose_name_plural = "Характеристики"
        ordering = ("name",)

    def __str__(self):
        return self.name


class ProductParameter(models.Model):
    """
    Значение характеристики конкретного товара
    у конкретного поставщика
    """

    product_info = models.ForeignKey(
        ProductInfo,
        on_delete=models.CASCADE,
        related_name="product_parameters",
        verbose_name="Информация о товаре",
    )
    parameter = models.ForeignKey(
        Parameter,
        on_delete=models.CASCADE,
        related_name="product_parameters",
        verbose_name="Характеристика",
    )
    value = models.CharField(
        max_length=255,
        verbose_name="Значение",
    )

    class Meta:
        verbose_name = "Характеристика товара"
        verbose_name_plural = "Характеристики товаров"
        constraints = [
            models.UniqueConstraint(
                fields=["product_info", "parameter"],
                name="unique_product_parameter",
            ),
        ]

    def __str__(self):
        return f"{self.parameter.name}: {self.value}"
