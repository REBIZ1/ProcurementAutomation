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
