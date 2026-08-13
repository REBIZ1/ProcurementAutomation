import yaml

from django.db import transaction

from products.models import (
    Shop,
    Category,
    Product,
    ProductInfo,
    Parameter,
    ProductParameter,
)


@transaction.atomic
def import_products_from_yaml(data, user):
    """
    Импортирует товары поставщика из YAML данных
    """
    shop_name = data["shop"]
    shop, _ = Shop.objects.update_or_create(
        user=user,
        defaults={
            "name": shop_name,
        },
    )
    categories = {}
    for category_data in data.get("categories", []):
        category, _ = Category.objects.update_or_create(
            id=category_data["id"],
            defaults={
                "name": category_data["name"],
            },
        )
        category.shops.add(shop)
        categories[category.id] = category
    ProductInfo.objects.filter(shop=shop).delete()
    for item in data.get("goods", []):
        category = categories.get(item["category"])
        if category is None:
            raise ValueError(
                f"Категория {item['category']} для товара {item['id']} не найдена."
            )
        product, _ = Product.objects.get_or_create(
            name=item["name"],
            category=category,
        )
        product_info = ProductInfo.objects.create(
            product=product,
            shop=shop,
            external_id=item["id"],
            model=item.get("model", ""),
            quantity=item["quantity"],
            price=item["price"],
            price_rrc=item["price_rrc"],
        )
        for parameter_name, parameter_value in item.get(
            "parameters",
            {},
        ).items():
            parameter, _ = Parameter.objects.get_or_create(
                name=parameter_name,
            )
            ProductParameter.objects.create(
                product_info=product_info,
                parameter=parameter,
                value=str(parameter_value),
            )
    return shop


def import_products_from_yaml_file(file_path, user):
    """
    Импортирует товары из локального YAML файла
    """
    with open(file_path, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)
    return import_products_from_yaml(
        data=data,
        user=user,
    )


def import_products_from_yaml_content(content, user):
    """
    Импортирует товары из содержимого YAML
    """
    data = yaml.safe_load(content)
    return import_products_from_yaml(
        data=data,
        user=user,
    )
