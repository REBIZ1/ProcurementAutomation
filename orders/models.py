from django.conf import settings
from django.db import models

from products.models import ProductInfo


class Cart(models.Model):
    """
    Корзина покупателя
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart",
        verbose_name="Покупатель",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата изменения",
    )

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"

    def __str__(self):
        return f"Корзина пользователя {self.user.email}"

    @property
    def total_sum(self):
        return sum(item.total_price for item in self.items.all())


class CartItem(models.Model):
    """
    Товар в корзине
    """

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Корзина",
    )
    product_info = models.ForeignKey(
        ProductInfo,
        on_delete=models.CASCADE,
        related_name="cart_items",
        verbose_name="Товар поставщика",
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name="Количество",
    )

    class Meta:
        verbose_name = "Товар корзины"
        verbose_name_plural = "Товары корзины"
        constraints = [
            models.UniqueConstraint(
                fields=["cart", "product_info"],
                name="unique_cart_product_info",
            ),
        ]

    def __str__(self):
        return f"{self.product_info.product.name} x {self.quantity}"

    @property
    def total_price(self):
        return self.product_info.price * self.quantity


class Contact(models.Model):
    """
    Контактные данные покупателя для доставки
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="contacts",
        verbose_name="Покупатель",
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name="Фамилия",
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name="Имя",
    )
    patronymic = models.CharField(
        max_length=150,
        blank=True,
        default="",
        verbose_name="Отчество",
    )
    email = models.EmailField(
        verbose_name="Email",
    )
    phone = models.CharField(
        max_length=30,
        verbose_name="Телефон",
    )
    city = models.CharField(
        max_length=100,
        verbose_name="Город",
    )
    street = models.CharField(
        max_length=150,
        verbose_name="Улица",
    )
    house = models.CharField(
        max_length=20,
        verbose_name="Дом",
    )
    building = models.CharField(
        max_length=20,
        blank=True,
        default="",
        verbose_name="Корпус",
    )
    structure = models.CharField(
        max_length=20,
        blank=True,
        default="",
        verbose_name="Строение",
    )
    apartment = models.CharField(
        max_length=20,
        blank=True,
        default="",
        verbose_name="Квартира",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
    )

    class Meta:
        verbose_name = "Контакт"
        verbose_name_plural = "Контакты"
        ordering = ("-created_at",)

    def __str__(self):
        return (
            f"{self.last_name} {self.first_name} — "
            f"{self.city}, {self.street}, {self.house}"
        )
