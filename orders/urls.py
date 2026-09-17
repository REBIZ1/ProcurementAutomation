from django.urls import path

from orders.views import (
    CartView,
    CartItemDeleteView,
    ContactListCreateView,
    ContactDetailView,
)

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
    path(
        "contacts/",
        ContactListCreateView.as_view(),
        name="contact-list-create",
    ),
    path(
        "contacts/<int:pk>/",
        ContactDetailView.as_view(),
        name="contact-detail",
    ),
]
