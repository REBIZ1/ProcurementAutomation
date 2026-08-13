from django.urls import path

from products.views import ShopUpdatePriceView, ShopStateView

urlpatterns = [
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
