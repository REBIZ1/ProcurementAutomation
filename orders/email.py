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


def send_order_invoice_email(order):
    """
    Отправляет накладную администратору для исполнения заказа
    """

    contact = order.contact
    subject = f"Накладная на заказ №{order.id}"
    lines = [
        f"Накладная на заказ №{order.id}",
        "",
        f"Дата заказа: {order.created_at.strftime('%d.%m.%Y %H:%M')}",
        f"Статус: {order.get_status_display()}",
        "",
        "Данные покупателя:",
        f"Фамилия: {contact.last_name}",
        f"Имя: {contact.first_name}",
        f"Отчество: {contact.patronymic}",
        f"Email: {contact.email}",
        f"Телефон: {contact.phone}",
        "",
        "Адрес доставки:",
        f"Город: {contact.city}",
        f"Улица: {contact.street}",
        f"Дом: {contact.house}",
        f"Корпус: {contact.building}",
        f"Строение: {contact.structure}",
        f"Квартира: {contact.apartment}",
        "",
        "Состав заказа:",
    ]
    for item in order.items.all():
        lines.append(
            f"- {item.product_name} | "
            f"Поставщик: {item.shop_name} | "
            f"{item.quantity} шт. | "
            f"{item.price} руб. | "
            f"Сумма: {item.total_price} руб."
        )
    lines.extend(
        [
            "",
            f"ИТОГО: {order.total_sum} руб.",
        ]
    )
    text_content = "\n".join(lines)
    html_items = ""
    for item in order.items.all():
        html_items += f"""
        <tr>
            <td>{item.product_name}</td>
            <td>{item.shop_name}</td>
            <td>{item.quantity}</td>
            <td>{item.price}</td>
            <td>{item.total_price}</td>
        </tr>
        """
    html_content = f"""
    <html>
        <body>
            <h2>Накладная на заказ №{order.id}</h2>
            <p>
                <strong>Дата заказа:</strong>
                {order.created_at.strftime("%d.%m.%Y %H:%M")}
            </p>
            <h3>Данные покупателя</h3>
            <p>
                {contact.last_name}
                {contact.first_name}
                {contact.patronymic}
            </p>
            <p>
                Email: {contact.email}<br>
                Телефон: {contact.phone}
            </p>
            <h3>Адрес доставки</h3>
            <p>
                {contact.city},
                {contact.street},
                дом {contact.house}
                {contact.building}
                {contact.structure}
                {contact.apartment}
            </p>
            <h3>Состав заказа</h3>
            <table border="1" cellpadding="5" cellspacing="0">
                <thead>
                    <tr>
                        <th>Товар</th>
                        <th>Поставщик</th>
                        <th>Количество</th>
                        <th>Цена</th>
                        <th>Сумма</th>
                    </tr>
                </thead>
                <tbody>
                    {html_items}
                </tbody>
            </table>
            <h3>
                Итого: {order.total_sum} руб.
            </h3>
        </body>
    </html>
    """
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[settings.ADMIN_ORDER_EMAIL],
    )
    email.attach_alternative(
        html_content,
        "text/html",
    )
    email.send(fail_silently=False)
