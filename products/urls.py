from django.urls import path

from products.views import ShopUpdatePriceView

urlpatterns = [
    path(
        "shop/update/",
        ShopUpdatePriceView.as_view(),
        name="shop-update",
    ),
]
