from django.conf import settings
from django.core.mail import EmailMultiAlternatives


def send_order_confirmation_email(order):
    user = order.user
    contact = order.contact
    subject = f"Подтверждение заказа №{order.id}"
    lines = [
        f"Здравствуйте, {contact.first_name}!",
        "",
        f"Ваш заказ №{order.id} успешно оформлен.",
        f"Статус: {order.get_status_display()}",
        "",
        "Состав заказа:",
    ]
    for item in order.items.all():
        lines.append(
            f"- {item.product_name} — "
            f"{item.quantity} шт. × {item.price} = "
            f"{item.total_price}"
        )

    lines.extend(
        [
            "",
            f"Итого: {order.total_sum}",
            "",
            "Адрес доставки:",
            f"{contact.city}, {contact.street}, {contact.house}",
        ]
    )
    text_content = "\n".join(lines)
    html_items = ""
    for item in order.items.all():
        html_items += f"""
        <li>
            {item.product_name} —
            {item.quantity} шт. × {item.price}
            = {item.total_price}
        </li>
        """
    html_content = f"""
    <html>
        <body>
            <h2>Заказ №{order.id}</h2>
            <p>
                Здравствуйте, {contact.first_name}!
            </p>
            <p>
                Ваш заказ успешно оформлен.
            </p>
            <p>
                <strong>Статус:</strong>
                {order.get_status_display()}
            </p>
            <h3>Состав заказа:</h3>
            <ul>
                {html_items}
            </ul>
            <p>
                <strong>Итого: {order.total_sum}</strong>
            </p>
            <h3>Адрес доставки:</h3>
            <p>
                {contact.city},
                {contact.street},
                {contact.house}
            </p>
        </body>
    </html>
    """

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    email.attach_alternative(
        html_content,
        "text/html",
    )
    email.send(fail_silently=False)
