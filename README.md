# Procurement Automation

Backend API для автоматизации закупок в розничной торговле.

Приложение позволяет покупателям регистрироваться, просматривать каталог товаров разных поставщиков, формировать корзину и оформлять заказы. Поставщики могут загружать прайс-листы, управлять доступностью приёма заказов и просматривать заказы, содержащие их товары.

## Стек

* Python 3.14+
* Django
* Django REST Framework
* PostgreSQL

---

# 1. Установка проекта

Клонировать проект:

```bash
git clone git@github.com:REBIZ1/ProcurementAutomation.git
```

Создать виртуальное окружение:

```bash
python -m venv .venv
```

Активировать его.

Linux/macOS:

```bash
source .venv/bin/activate
```

Windows:

```bash
.venv\Scripts\activate
```

Установить зависимости:

```bash
pip install -r requirements.txt
```

---

# 2. Настройка `.env`

В корне проекта рекомендуется создать файл:

```text
.env
```

Пример:

```env
SECRET_KEY=
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

DB_NAME=procurement
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432

EMAIL_BACKEND=
EMAIL_HOST=
EMAIL_PORT=
EMAIL_USE_TLS=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=
```

Если используется Gmail, для SMTP необходимо использовать пароль приложения, а не обычный пароль от аккаунта.

---

# 3. Настройка базы данных

```bash
python manage.py makemigrations
```

Затем:

```bash
python manage.py migrate
```

Запустить сервер:

```bash
python manage.py runserver
```

После запуска API доступно по адресу:

```text
http://127.0.0.1:8000/
```
