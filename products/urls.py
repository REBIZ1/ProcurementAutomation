from django.urls import path

from products.views import (
    ShopUpdatePriceView,
    ShopStateView,
    ProductListView,
    ProductDetailView,
)

urlpatterns = [
    path(
        "products/",
        ProductListView.as_view(),
        name="product-list",
    ),
    path(
        "products/<int:pk>/",
        ProductDetailView.as_view(),
        name="product-detail",
    ),
    path(
        "shop/update/",
        ShopUpdatePriceView.as_view(),
        name="shop-update",
    ),
    path(
        "shop/state/",
        ShopStateView.as_view(),
        name="shop-state",
    ),
]
