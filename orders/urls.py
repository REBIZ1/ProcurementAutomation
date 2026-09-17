from django.urls import path

from orders.views import CartView, CartItemDeleteView

urlpatterns = [
    path(
        "cart/",
        CartView.as_view(),
        name="cart",
    ),
    path(
        "cart/items/<int:pk>/",
        CartItemDeleteView.as_view(),
        name="cart-item-delete",
    ),
]
