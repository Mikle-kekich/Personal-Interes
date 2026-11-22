# Система управления личными интересами (Interest Tracker)

Приложение, в котором пользователи подписываются на интересы (хобби) из разных категорий, отмечают занятия по подписке и следят за выполнением недельного плана. Консольная версия (ПР3) дополнена веб-интерфейсом на Django (ПР5): интересы и подписки можно просматривать в браузере. Страницы веб-интерфейса формируются шаблонами Django (ПР6). Данные хранятся в базе данных SQLite (ПР7); с ПР9 все страницы получают их через Django ORM: таблицы описаны моделями Django, структура базы управляется миграциями.


## Практическая работа 10

Django Admin и Django ORM реализованы для предметной области личных интересов.
Модели Room/User/Booking из учебного примера соответствуют Interest/User/Subscription.
Веб-приложение использует `db.sqlite3`; консольный пакет `models/` и исходная база ПР7 сохранены.

- Все пять моделей зарегистрированы в `/admin/`. Настроены столбцы, поиск, фильтры, сортировка, страницы по 10 записей, русские подписи, inline подписок в карточках пользователя и интереса, inline занятий в подписке.
- `Subscription.Status`: ACTIVE, CANCELLED, COMPLETED. Менеджер `SubscriptionManager` и `SubscriptionQuerySet`: `active()`, `cancelled()`, `completed()`, `for_date()`.
- Миграции `subscriptions/0002–0004` добавляют статус, переносят булев признак и удаляют его. История и идентификаторы сохраняются; ограничения базы запрещают повторную активную подписку и неизвестный статус. Админ-форма также проверяет архивный интерес. При программном создании для этой проверки нужно вызывать `full_clean()`.
- `Interest.slug`, `get_absolute_url()`: транслитерация Unidecode, уникальные адреса `/interests/<slug>/`. Старые числовые адреса продолжают работать под именем `interests:detail_by_id`. Для существующих записей используется суффикс ID, для новых — UUID; переименование не меняет адрес. `bulk_create()` для Interest не используется, поскольку он обходит `save()`.
- `Interest.is_intensive` — GeneratedField (сохраняемый столбец SQLite), план не менее 5 часов в неделю; пересчитывается базой. Миграции `interests/0002–0004` добавляют поле, заполняют slug и вводят уникальность.
- Контекстный процессор `interest_context` передаёт `app_title` и `catalog_interests_count`; счётчик показан в навигации.
- Список `/subscriptions/`: `status=ACTIVE|CANCELLED|COMPLETED|all` (по умолчанию ACTIVE), фильтры date, interest, user, сортировка sort=date|interest|user, страницы по 3 записи. Ссылки `{% querystring %}` сохраняют условия.
- `/interests/available/?user=1&date=2026-09-14`: активная подписка с датой начала не позднее выбранной блокирует повторную подписку этого пользователя. CANCELLED и COMPLETED не блокируют. Без даты проверяются все текущие активные подписки. Это подписки на интересы, а не брони на отдельный день; история момента отмены не моделируется.
- Статистика считает все три статуса; часы сохраняются независимо от отмены и завершения.
- Список подписок использует `annotate(F())` и `values()`, детали — `select_related()`. Загрузка пользователя, интереса и категории: 4 SQL-запроса без JOIN и 1 с JOIN. Карточка интереса использует один набор ID подписчиков вместо запроса для каждого пользователя.

### Запуск и проверки ПР10

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
# Только для первичного переноса данных ПР7 в новую базу:
# .\.venv\Scripts\python.exe db/import_sqlite_to_orm.py
.\.venv\Scripts\python.exe manage.py createsuperuser
$env:DJANGO_DEBUG='1'
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

Сайт открывается по адресу http://127.0.0.1:8000/, административная панель — http://127.0.0.1:8000/admin/.
Используется прежний стандартный порт 8000, как в методичке ПР10.
Debug Toolbar включается только при `DJANGO_DEBUG=1` с локального IP и отключается в тестах.
При `DJANGO_DEBUG=0` используется стандартная страница 404, маршруты панели не подключаются.
В SQL-вкладке списка подписок видны JOIN, COUNT для пагинации и общего числа активных записей,
LIMIT/OFFSET и два справочных запроса. Контекстный процессор добавляет один COUNT.
Детали подписки: 3 запроса (JOIN, сумма часов и счётчик навигации).
Не запускайте перенос ПР7 повторно после редактирования данных через админ-панель: импорт обновляет записи исходными значениями.

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe manage.py test -v 2
.\.venv\Scripts\python.exe -m pytest -v
.\.venv\Scripts\python.exe -m flake8 .
.\.venv\Scripts\python.exe docs/pr10/verify_orm.py
```

Результат 14.11.2026: 22 Django-теста и 17 прежних pytest-тестов проходят; миграции актуальны.
Проверяются статусы, доступность на одну дату, фильтры и пагинация, 404, slug, GeneratedField,
права и формы Admin, ограничение числа SQL-запросов и миграция старых данных.
Протоколы проверок находятся в `docs/pr10/`. Резервная копия локальной базы и данные входа
не включаются в Git (`.pr10/`, `db.sqlite3`).

Справка: [Django GeneratedField](https://docs.djangoproject.com/en/5.2/ref/models/fields/#generatedfield),
[Django Admin](https://docs.djangoproject.com/en/5.2/ref/contrib/admin/),
[Debug Toolbar](https://django-debug-toolbar.readthedocs.io/en/latest/installation.html).

## Назначение
Приложение предназначено для структурирования, учёта и отслеживания личных интересов, хобби и направлений саморазвития пользователя. Система помогает планировать время на увлечения, ставить цели по обучению или практике, а также контролировать регулярность занятий.

## Используемые технологии
- Python 3;
- Django 5.2 — веб-фреймворк;
- Django Template Language — шаблоны веб-страниц;
- HTML — разметка веб-страниц;
- CSS и Bootstrap 5.3 (подключается через CDN) — оформление страниц, собственный CSS проекта;
- JavaScript — небольшое клиентское поведение (год в подвале);
- JSON — исходные данные проекта и хранилище консольной версии;
- SQLite и язык SQL — реляционная база данных; в ПР7 работа с ней шла напрямую через модуль `sqlite3`, с ПР9 — через Django ORM (модели и миграции);
- django-debug-toolbar — панель со списком SQL-запросов страницы (для проверки ORM-запросов);
- pytest — автоматизированные тесты;
- flake8 — проверка качества кода.

## Целевая аудитория
Люди, стремящиеся осознанно управлять своим свободным временем, студенты, специалисты в процессе самообразования и смены квалификации, а также все, кто хочет гармонично совмещать несколько разнородных увлечений (спорт, творчество, профессиональное развитие, чтение).

## Предметная область
Личная продуктивность, тайм-менеджмент и организация свободного времени. Интересы собраны в каталог и разделены по категориям. Пользователь подписывается на интересы, отмечает по подписке занятия (дата и часы) и видит прогресс выполнения недельного плана.

Правила предметной области:
- у одного пользователя не может быть двух активных подписок на один интерес;
- отменённая подписка не удаляется: она остаётся в списке и не мешает подписаться снова;
- на интерес в архиве подписаться нельзя;
- занятие можно отметить только по активной подписке, время одного занятия — от 0 до 24 ч;
- недельная цель интереса — от 0 до 168 ч, неделя считается по календарю (понедельник — воскресенье).

## Основные сущности
Пользователь, интерес, категория, подписка. Каждая сущность — отдельный класс в своём файле пакета `models/`. Те же сущности (и занятия по подписке) описаны моделями Django — см. раздел «Модели Django и ORM (ПР9)»; пакет `models/` остаётся основой консольной версии.

### `Category` — категория (`models/categories.py`)
Сфера интересов, например «Спорт» или «Языки».
- Атрибуты: `id` — номер, `name` — название.
- Методы: `__str__()` — строковое представление.

### `Interest` — интерес (`models/interests.py`)
Хобби или направление саморазвития из каталога.
- Атрибуты: `id`, `name`, `category` — объект `Category`, `weekly_goal` — план на неделю в часах, `is_active` — интерес активен (`False` — в архиве).
- Методы: `validate_weekly_goal()` — проверка недельной цели (`@staticmethod`), `__str__()`.

### `User` — пользователь (`models/users.py`)
- Атрибуты: `id`, `name` — имя, `email` — адрес электронной почты.
- Методы: `from_data()` — создание пользователя из словаря JSON (`@classmethod`), `__str__()`.

### `Subscription` — подписка (`models/subscriptions.py`)
Главная сущность: подписка пользователя на интерес с журналом занятий.
- Атрибуты: `id`, `user` — объект `User`, `interest` — объект `Interest`, `start_date` — дата подписки, `is_cancelled` — признак отмены, `hours_by_date` — журнал занятий `{дата: часы}`.
- Методы: `cancel()` — отменить подписку, `add_activity()` — отметить занятие, `get_weekly_hours()` — часы за неделю, `get_total_hours()` — все часы по подписке, `status` — «активна» или «отменена» (`@property`), `__str__()`.

## Взаимодействие объектов
Подписка хранит ссылки на объекты пользователя и интереса, а интерес — ссылку на объект категории:
```text
Subscription
├── user     → User
└── interest → Interest
               └── category → Category
```
Поэтому данные связанных объектов доступны напрямую: `subscription.user.name`, `subscription.interest.weekly_goal`, `subscription.interest.category.name`. Проверка «можно ли подписаться» (`can_subscribe()`) использует состояние интереса (`interest.is_active`) и других подписок (`subscription.is_cancelled`).

Принципы ООП в проекте:
- **инкапсуляция** — данные и поведение объединены в объекте: подписка сама меняет своё состояние методами `cancel()` и `add_activity()` и проверяет при этом правила;
- **композиция** — `Subscription` содержит объекты `User` и `Interest`, `Interest` содержит объект `Category`;
- **полиморфизм** — у каждого класса свой `__str__()`, поэтому `print(объект)` работает для любой сущности;
- **наследование** не используется: между сущностями нет отношения «является» (подписка не является пользователем или интересом).

## Функции ПР1 и ПР2 после перехода к ООП
| Было в ПР2 | Стало в ПР3 |
|---|---|
| интерес и запись активности — словари | объекты `Interest` и `Subscription` |
| категория — строка в словаре интереса | объект `Category` |
| `add_interest()`, `find_interests()`, `sort_interests()` | те же функции, работают со списком объектов `Interest` |
| `get_interest()` | `find_interest_by_id()` — возвращает объект или `None` |
| `is_interest_active()` | атрибут `Interest.is_active`, проверка в `can_subscribe()` |
| проверка недельной цели в `add_interest()` | метод `Interest.validate_weekly_goal()` |
| `add_activity()`, `get_weekly_hours()` | методы `Subscription.add_activity()`, `Subscription.get_weekly_hours()` |
| `cancel_activity()` — удаление записи | `Subscription.cancel()` — подписка остаётся в списке, меняется состояние |
| `calculate_progress()`, `generate_recommendation()` (ПР1) | остались обычными функциями: считают по переданным числам |
| `display_interest_card()` (ПР1) | принимает объект `Subscription` |
| `get_statistics()` | считает часы по подпискам |
| `load_...()`, `save_...()` | преобразуют JSON в объекты и обратно |
| `input_int()`, `input_float()`, `input_date()` | остались вспомогательными функциями |

## Переход от консоли к вебу (ПР5)
Консольная версия (`main.py`) сохранена и работает как раньше. Веб-интерфейс добавлен рядом с ней и использует те же классы, функции и JSON-файлы:

| ПР3 — консольное приложение | ПР5 — веб-приложение |
|---|---|
| консольное меню | веб-интерфейс: страницы и ссылки |
| `input()` | HTTP-запрос по адресу (URL) |
| вывод в консоль (`print()`) | HTML-страница в HTTP-ответе |
| функция сценария | view-функция |
| запуск `python main.py` | запуск `python manage.py runserver` |
| JSON — основное хранилище | JSON временно остаётся хранилищем, база данных появится позже |

Django-проект `interest_tracker` создан в корне существующего репозитория, рядом с кодом ПР1–ПР3. Он состоит из Django-приложений (с ПР9 их четыре, добавлено `users`):
- `homepage` — главная страница и общий каркас всех страниц;
- `interests` — страницы интересов (категория показывается в интересе как его атрибут);
- `subscriptions` — страницы подписок;
- `users` — модель пользователя (добавлено в ПР9).

В ПР5 отдельного приложения для пользователей не было: пользователи ПР3 (класс `User`) загружались из `data/users.json`. В ПР9 добавлено приложение `users` с моделью `User` — пользователем предметной области. Это не встроенная модель аутентификации Django (`django.contrib.auth`): работа с ней (регистрация, вход, разграничение доступа) будет рассмотрена в следующих темах.

Не следует путать пакет `models/` (классы предметной области ПР3: консольная версия и тесты) и файлы `models.py` Django-приложений (модели ORM, ПР9): это разные классы с одинаковыми именами `Category`, `Interest`, `User`, `Subscription`; веб-страницы используют только модели Django.

## Страницы веб-интерфейса
- `/` — главная страница: описание приложения и кнопки-ссылки на разделы (view-функция `index()`);
- `/interests/` — список интересов **через Django ORM**: категория, план на неделю, статус; ссылки-фильтры по категориям (`?category=<номер>`) и поиск по названию интереса или категории (`?q=<текст>`) (view-функция `interests()`);
- `/interests/available/` — **поиск доступных интересов**: по выбранному пользователю (`?user=<номер>`) показываются активные интересы, на которые у него нет действующей подписки (`filter()` и `exclude()`) (view-функция `available_interests()`);
- `/interests/<int:interest_id>/` — страница интереса: категория, план, статус и проверка `Interest.can_subscribe()` для каждого пользователя (view-функция `interest_detail()`);
- `/subscriptions/` — активные подписки **через Django ORM**: пользователь, интерес, дата, статус; фильтры по дате подписки (`?date=ГГГГ-ММ-ДД`), интересу (`?interest=<номер>`) и пользователю (`?user=<номер>`), сортировка (`?sort=date|interest|user`), постраничный вывод по 3 подписки (`?page=<номер>`) и количество подписок (view-функция `subscriptions()`);
- `/subscriptions/statistics/` — **статистика**: занятия и часы, активные подписки и часы по интересам, интересы по категориям, категории с несколькими интересами (`aggregate()`, `annotate()`, `Count`, `Sum`) (view-функция `statistics()`);
- `/subscriptions/<int:subscription_id>/` — страница подписки: связанные пользователь, интерес и категория (`select_related()`), дата, всего часов, статус (view-функция `subscription_detail()`).

Если интерес или подписка с указанным номером не найдены, `get_object_or_404()` прерывает обработку, а Django возвращает ответ 404, который оформляет `handler404` (см. ниже); тот же обработчик отвечает на адреса, которых нет среди маршрутов. Ссылки навигации («Главная», «Интересы», «Подписки», «Статистика») есть на каждой странице, из списков можно перейти к карточкам, из карточки подписки — к карточке интереса. Номера записей в базе Django совпадают с номерами в JSON и в базе ПР7 (при переносе сохраняются `id`). Подробнее — в разделе «Модели Django и ORM (ПР9)».

Как запрос доходит до страницы (на примере `/interests/1/`):
```text
браузер: GET /interests/1/
→ interest_tracker/urls.py: path("interests/", include("interests.urls"))
→ interests/urls.py: path("<int:interest_id>/", views.interest_detail, name="detail_by_id")
→ interest_detail(request, interest_id=1): get_object_or_404(), Interest.can_subscribe() для каждого пользователя, подготовка контекста
→ render(): шаблон interests/interest_detail.html, который наследует templates/base.html
→ HttpResponse: HTML-страница и код статуса 200
```

HTML веб-страниц находится в шаблонах Django (см. раздел «Шаблоны Django (ПР6)»); view-функции HTML не формируют. Функция `page()` из ПР5 удалена.

### Обработка ошибки 404, DEBUG и ALLOWED_HOSTS
В `interest_tracker/settings.py` заданы `DEBUG = False` и `ALLOWED_HOSTS = ['127.0.0.1', 'localhost']`, в `interest_tracker/urls.py` — `handler404 = 'homepage.views.page_not_found'`.
- Адрес не подошёл ни под один маршрут (`/abc/`, `/interests/abc/`): Django получает `Resolver404` и вызывает обработчик `handler404` — функцию `page_not_found(request, exception)` (`homepage/views.py`). Она отображает шаблон `homepage/page_not_found.html` («Страница не найдена») с кодом 404. Без `handler404` Django использовал бы стандартный `django.views.defaults.page_not_found` с простой страницей «Not Found».
- Маршрут найден, но объекта нет (`/interests/999/`): `get_object_or_404()` вызывает `Http404`, и Django передаёт его в тот же `handler404`: страница «Страница не найдена» с кодом 404. До ПР9 view сама передавала `status=404` и показывала сообщение «Интерес не найден».
- Пользовательский `handler404` работает только при `DEBUG = False`; при `DEBUG = True` Django показывает свою техническую страницу 404 со списком маршрутов.
- При `DEBUG = False` Django требует непустой `ALLOWED_HOSTS`: без него `runserver` не запускается (`You must set settings.ALLOWED_HOSTS if DEBUG is False`), а запросы с чужим именем хоста получают ответ 400. В списке — имена, по которым открывают сайт: `http://127.0.0.1:8000/` и `http://localhost:8000/`.
- При `DEBUG = False` сервер разработки не раздаёт статические файлы. Поэтому для просмотра сайта с собственным CSS, JavaScript и логотипом (ПР6) сервер запускают с флагом `--insecure`: `python manage.py runserver --insecure`. Для отладки (подробные страницы ошибок с трассировкой) можно временно поставить `DEBUG = True`: тогда статика раздаётся и без флага, но пользовательский `handler404` не работает.

## Шаблоны Django (ПР6)
В ПР6 слой представления веб-части перестроен: HTML перенесён из Python-строк в шаблоны Django. Источник данных не изменился — JSON-файлы и объекты ПР3; Django ORM и формы пока не используются.

| ПР5 | ПР6 |
|---|---|
| HTML-страница собирается в Python-строке функцией `page()` | HTML лежит в файлах `.html` каталогов `templates/` |
| view возвращает `HttpResponse(page(...))` | view готовит контекст и вызывает `render(request, "шаблон.html", context)` |
| общий каркас — функция `page()` | общий каркас — базовый шаблон `templates/base.html` |
| повторяющийся HTML копируется в f-строках | повторяющиеся фрагменты вынесены через `{% include %}` |
| ссылки записаны адресами: `href="/interests/"` | ссылки строятся тегом `{% url 'interests:list' %}` |
| оформление — Bootstrap по CDN | Bootstrap + собственные `style.css`, `main.js`, `logo.png` |

### Базовый шаблон и наследование
`templates/base.html` содержит общую структуру страницы: `<!DOCTYPE html>`, кодировку и `viewport`, подключение Bootstrap и собственного CSS, шапку с логотипом и навигацией, контейнер `<main>`, подвал и подключение `main.js`. Дочерние шаблоны начинаются с `{% extends "base.html" %}` и переопределяют два блока:
```text
{% block title %}...{% endblock %}    — заголовок вкладки браузера
{% block content %}...{% endblock %}  — содержимое страницы
```
Каталог шаблонов уровня проекта указан в `settings.py`: `TEMPLATES[0]["DIRS"] = [BASE_DIR / "templates"]`; шаблоны приложений Django находит сам (`APP_DIRS = True`).

### Включаемые шаблоны
- `templates/includes/navigation.html` — навигация, подключается в `base.html`;
- `interests/includes/interest_card.html` — карточка одного интереса; `interest_list.html` подключает её в цикле `{% for interest in interests %}`, поэтому внутри карточки доступна переменная `interest`;
- `subscriptions/includes/subscription_status.html` — статус подписки (активна или отменена); используется и в списке подписок, и на странице подписки.

Подключение: `{% include "interests/includes/interest_card.html" %}`.

### Контекст, циклы и условия
View передаёт данные словарём. Например, `interests()`:
```python
context = {"interests": Interest.objects.order_by("name")}
return render(request, "interests/interest_list.html", context)
```
В шаблоне имена ключей контекста становятся переменными: `{% for interest in interests %}`, `{{ interest.name }}`, `{{ interest.category.name }}`. Для пустой коллекции используется `{% empty %}` («Интересы не найдены.», «Подписки не найдены.»). Условия `{% if %}` выбирают вид страницы и значков: интерес активен или в архиве, статус подписки (`subscription.status`, три состояния), можно или нельзя подписаться (`item.allowed`), найден ли объект. Проверка `can_subscribe()` вызывается во view (шаблон не вычисляет правила), результат передаётся в контексте списком `users_info`.

Если объект не найден, view вызывает `get_object_or_404()`: Django возвращает ответ 404 (страница «Страница не найдена»), поэтому шаблон карточки получает только существующий объект. (В ПР6 view передавала `None`, шаблон показывал сообщение через `{% if interest %} ... {% else %} ... {% endif %}`, а код 404 задавался параметром `status`.)

### Фильтры шаблонов
- `{{ interests|length }}` и `{{ subscriptions|length }}` — количество элементов («Всего интересов: 6»);
- `{{ interest.name|default:"Без названия" }}` — значение по умолчанию для пустого названия;
- `{{ interest.weekly_goal|floatformat:1 }}` — число с одним знаком после запятой («8,0 ч»; запятая — из настройки `LANGUAGE_CODE = 'ru-RU'`).

Фильтры используются только для представления данных, бизнес-логика остаётся в Python. Даты подписок в моделях Django — объекты `date` (поле `DateField`), поэтому в шаблонах работает фильтр `date`: `{{ subscription.start_date|date:"d.m.Y" }}` выводит «08.09.2026». В JSON даты остаются строками `ГГГГ-ММ-ДД`; консольная версия показывает дату как `ДД.ММ.ГГГГ`.

### Именованные URL и пространства имён
В `urls.py` каждого приложения задан `app_name` и имена маршрутов; ссылки в шаблонах строятся тегом `{% url %}`, адреса в HTML не записаны:

| Имя маршрута | Адрес | Пример в шаблоне |
|---|---|---|
| `homepage:index` | `/` | `{% url 'homepage:index' %}` |
| `interests:list` | `/interests/` | `{% url 'interests:list' %}` |
| `interests:detail` | `/interests/<slug:slug>/` | `{{ interest.get_absolute_url }}` |
| `subscriptions:list` | `/subscriptions/` | `{% url 'subscriptions:list' %}` |
| `subscriptions:detail` | `/subscriptions/<int:subscription_id>/` | `{% url 'subscriptions:detail' subscription.id %}` |

Если изменить адрес маршрута в `urls.py`, ссылки в шаблонах обновятся сами; если изменить `app_name` или `name`, нужно согласованно поменять и вызовы `{% url %}`.

### Статические файлы
Собственные статические файлы проекта находятся в `homepage/static/homepage/`:

| Файл | Назначение | Где используется |
|---|---|---|
| `css/style.css` | оформление шапки, логотипа, карточки интереса, статуса подписки | `base.html`, `interest_card.html`, `subscription_status.html` |
| `js/main.js` | подставляет текущий год в подвал страницы | `base.html` |
| `img/logo.png` | логотип в шапке | `base.html` |

В шаблонах подключается `{% load static %}` и используется `{% static 'homepage/css/style.css' %}`. Проверить поиск файла можно командой `python manage.py findstatic homepage/img/logo.png`.

## Основные операции
### Используется в веб-интерфейсе (ПР5–ПР9)
- просмотр списка интересов, отбор по категории и поиск по названию или категории (ORM);
- поиск интересов, доступных для подписки пользователю (ORM);
- просмотр страницы интереса и проверка правил подписки для каждого пользователя (ORM, `Interest.can_subscribe()`);
- просмотр активных подписок: фильтры по дате, интересу и пользователю, сортировка, постраничный вывод (ORM);
- просмотр страницы подписки со связанными объектами и суммой часов (ORM);
- статистика: занятия, часы по интересам, подписки и интересы по категориям (ORM).

### Консольная версия (ПР3)
Подписки (главная функция):
- оформление подписки пользователя на интерес с проверкой правил (`create_subscription()`);
- отмена подписки (`cancel_subscription()` → `Subscription.cancel()`);
- просмотр подписок;
- отметка занятия по подписке (дата и часы);
- прогресс по подписке за неделю: карточка интереса и рекомендация;
- статистика: часы по каждому интересу и общий итог.

Интересы и категории:
- просмотр интересов, поиск по названию, сортировка по недельной цели;
- отбор интересов по категории;
- добавление интереса (с выбором категории) и добавление категории.

Пользователи:
- просмотр пользователей, поиск по имени или почте, добавление пользователя.

### Отложено до следующих работ
Эти операции реализованы в консольной версии. В веб-интерфейсе они появятся, когда будут добавлены формы и POST-запросы:
- оформление и отмена подписки;
- отметка занятия по подписке;
- прогресс за неделю и рекомендация;
- сортировка интересов по недельной цели (поиск интересов по названию в вебе есть с ПР9);
- добавление интереса, категории и пользователя, поиск пользователя.

## Хранение данных
Данные хранятся в JSON-файлах каталога `data/`: `categories.json`, `interests.json`, `users.json`, `subscriptions.json`. Даты записаны строкой `ГГГГ-ММ-ДД`. С ПР7 те же данные перенесены в базу SQLite `data/interest_tracker.sqlite`, а с ПР9 — в базу Django `db.sqlite3` (разделы «База данных SQLite (ПР7)» и «Модели Django и ORM (ПР9)»): все веб-страницы читают базу Django через ORM, консольная версия работает с JSON.

При загрузке (`storage.py`) данные JSON преобразуются в объекты `Category`, `Interest`, `User` и `Subscription`, при сохранении — обратно в словари. Вместо связанных объектов в JSON записываются их номера: `category_id`, `user_id`, `interest_id`. При загрузке по номерам находятся объекты из уже загруженных списков; запись со ссылкой на несуществующий объект пропускается. Если файла нет, программа начинает с пустых данных; если файл повреждён, выводится сообщение и данные из него не загружаются. Данные сохраняются после каждого изменения.

До ПР9 страницы интереса и подписки читали JSON функцией `load_data()` из `homepage/views.py`; после перехода на ORM она не нужна и удалена. JSON-файлы используют консольная версия и скрипт переноса `db/import_json.py` (ПР7).

`data/interests.json`:
```json
[
    {
        "id": 1,
        "name": "Изучение веб-разработки на Python",
        "category_id": 1,
        "weekly_goal": 8.0,
        "is_active": true
    }
]
```

`data/subscriptions.json`:
```json
[
    {
        "id": 1,
        "user_id": 1,
        "interest_id": 1,
        "start_date": "2026-09-08",
        "is_cancelled": false,
        "hours_by_date": {
            "2026-09-08": 2.0,
            "2026-09-10": 2.0
        }
    }
]
```

## База данных SQLite (ПР7)
В ПР7 проект получил слой реляционного хранения данных: файл базы `data/interest_tracker.sqlite`, SQL-запросы и их использование в Django-представлениях. Работа идёт напрямую через SQL и модуль `sqlite3` стандартной библиотеки Python, Django ORM на тот момент не использовался (служебный файл `db.sqlite3` Django был отдельной базой и к данным проекта не относился). JSON-файлы остаются в проекте: из них данные один раз переносятся в базу, а консольная версия (`main.py`) продолжает работать с ними.

Путь данных на веб-страницах: SQLite → SQL-запрос → `sqlite3` во view-функции → контекст → шаблон → страница.

> С ПР9 веб-страницы получают данные через Django ORM из базы Django `db.sqlite3` (раздел «Модели Django и ORM (ПР9)»). Файлы `sql/schema.sql`, `sql/queries.sql`, `db/database.py` и `db/import_json.py` сохранены как предыдущая реализация, а `data/interest_tracker.sqlite` — как источник данных для переноса в ORM. Ниже описана работа ПР7.

### Структура базы данных
Пять таблиц: по таблице на сущность ПР3 и таблица занятий. В JSON занятия лежат внутри подписки (словарь `hours_by_date`), в реляционной базе их выносят в отдельную таблицу `activities`: одна запись — одно занятие.

| Таблица | Поля и типы |
|---|---|
| `categories` | `id` INTEGER PRIMARY KEY; `name` TEXT NOT NULL |
| `users` | `id` INTEGER PRIMARY KEY; `name` TEXT NOT NULL; `email` TEXT NOT NULL |
| `interests` | `id` INTEGER PRIMARY KEY; `name` TEXT NOT NULL; `category_id` INTEGER NOT NULL (внешний ключ); `weekly_goal` REAL NOT NULL; `is_active` INTEGER NOT NULL DEFAULT 1 (1 — активен, 0 — в архиве) |
| `subscriptions` | `id` INTEGER PRIMARY KEY; `user_id` INTEGER NOT NULL (внешний ключ); `interest_id` INTEGER NOT NULL (внешний ключ); `start_date` TEXT NOT NULL (`ГГГГ-ММ-ДД`); `is_cancelled` INTEGER NOT NULL DEFAULT 0 (0 — активна, 1 — отменена) |
| `activities` | `id` INTEGER PRIMARY KEY; `subscription_id` INTEGER NOT NULL (внешний ключ); `activity_date` TEXT NOT NULL; `hours` REAL NOT NULL |

Первичный ключ `id` однозначно определяет запись таблицы. Внешние ключи (`FOREIGN KEY ... REFERENCES`) связывают таблицы:
```text
interests.category_id      → categories.id
subscriptions.user_id      → users.id
subscriptions.interest_id  → interests.id
activities.subscription_id → subscriptions.id
```
Логические значения хранятся числами 0 и 1, даты — строками `ГГГГ-ММ-ДД` (такие строки можно сравнивать и сортировать средствами SQL). Поля `NOT NULL` не допускают пустого значения.

### Файлы слоя базы данных
- `sql/schema.sql` — команды `CREATE TABLE IF NOT EXISTS` для пяти таблиц (`IF NOT EXISTS` позволяет выполнять схему повторно без ошибки);
- `db/database.py` — `get_connection()`: подключение к `data/interest_tracker.sqlite` и `PRAGMA foreign_keys = ON` (по умолчанию SQLite не проверяет внешние ключи); путь строится от расположения файла, а не от текущего каталога;
- `db/import_json.py` — однократный перенос данных из JSON: по функции на таблицу, вставка `executemany()` с параметрами `?`, `int()` для логических значений, `commit()` при успехе и `rollback()` при ошибке. Порядок импорта: категории и пользователи, затем интересы, подписки и занятия — запись со ссылкой на ещё не созданную запись вставить нельзя. Повторный запуск завершится ошибкой `UNIQUE constraint failed`, транзакция откатится, база не изменится;
- `sql/queries.sql` — 15 проверенных запросов с комментариями (см. ниже);
- `data/interest_tracker.sqlite` — файл базы данных (хранится в Git).

### Создание базы и перенос данных
Команды выполняются из корня проекта. Файл базы уже есть в репозитории; чтобы создать его заново, удалите старый файл (`Remove-Item .\data\interest_tracker.sqlite`) и выполните:
```text
python -c "import sqlite3; sqlite3.connect('data/interest_tracker.sqlite').close()"
python -c "import sqlite3; conn=sqlite3.connect('data/interest_tracker.sqlite'); sql=open('sql/schema.sql', encoding='utf-8').read(); conn.executescript(sql); conn.commit(); conn.close()"
python -m db.import_json
```
Первая команда создаёт пустой файл, вторая выполняет схему, третья переносит данные. Проверка после импорта — количество записей совпадает с JSON:

| Таблица | Записей | Источник |
|---|---|---|
| `categories` | 5 | `categories.json` |
| `users` | 2 | `users.json` |
| `interests` | 6 | `interests.json` |
| `subscriptions` | 6 | `subscriptions.json` |
| `activities` | 12 | пары «дата: часы» в `hours_by_date` всех подписок |

Запросы проверяются в консоли SQLite. Если `sqlite3` не установлен, подойдёт консоль, встроенная в Python 3.12+:
```text
python -m sqlite3 data/interest_tracker.sqlite
```
После приглашения `sqlite>` можно вставлять запросы из `sql/queries.sql`; выход — `.exit`.

### SQL-запросы (`sql/queries.sql`)
В файле запросы пронумерованы и снабжены комментариями; в запросах подставлены значения для проверки (категория 2, пользователь 1), в приложении они передаются параметрами `?`.

| № | Запрос | Элементы SQL | Где используется |
|---|---|---|---|
| 1 | список категорий | SELECT, ORDER BY | фильтр на `/interests/` |
| 2 | список пользователей | SELECT, ORDER BY | выбор пользователя на `/interests/available/` |
| 3 | список интересов | SELECT, ORDER BY | учебный |
| 4 | активные интересы с целью от 4 ч | WHERE (`AND`) | учебный |
| 5 | пользователь по номеру | WHERE, параметр | `/interests/available/` |
| 6 | интересы с названиями категорий | JOIN | `/interests/` |
| 7 | интересы выбранной категории | JOIN, WHERE, параметр | `/interests/?category=<номер>` |
| 8 | активные подписки с пользователем и интересом | JOIN (две таблицы), WHERE | `/subscriptions/` |
| 9 | интересы, доступные пользователю | JOIN, WHERE, подзапрос `NOT IN`, параметр | `/interests/available/` |
| 10 | количество активных подписок | COUNT, WHERE | `/subscriptions/` |
| 11 | количество занятий и сумма часов | COUNT, SUM, COALESCE | `/subscriptions/statistics/` |
| 12 | активные подписки по интересам | LEFT JOIN, COUNT, GROUP BY | `/subscriptions/statistics/` |
| 13 | часы занятий по интересам | LEFT JOIN, SUM, COALESCE, GROUP BY | `/subscriptions/statistics/` |
| 14 | интересы по категориям | LEFT JOIN, COUNT, GROUP BY | `/subscriptions/statistics/` |
| 15 | категории с несколькими интересами | JOIN, GROUP BY, HAVING | `/subscriptions/statistics/` |

Пояснения:
- `LEFT JOIN` в запросах 12–14 оставляет в результате интересы и категории, у которых нет связанных записей (в счётчике будет 0), а обычный `JOIN` в запросе 15 их отбрасывает;
- `WHERE` фильтрует отдельные записи до группировки, `HAVING` — группы после неё;
- запрос 9 повторяет правило `can_subscribe()`: подписаться можно на активный интерес, если у пользователя нет его активной подписки; результат совпадает с проверкой на Python для обоих пользователей;
- `COALESCE(SUM(...), 0)` заменяет `NULL` нулём: у интереса без занятий сумма не определена;
- часы в запросе 13 считаются по всем подпискам, включая отменённые, как в консольной статистике (`get_statistics()`), общий итог — 22,0 ч.

### Получение данных из SQLite в Django
Каждая view-функция открывает соединение через `get_connection()`, включает `conn.row_factory = sqlite3.Row`, выполняет запрос, получает строки методом `fetchall()` (или `fetchone()`), закрывает соединение и передаёт результат в шаблон через контекст:
```python
conn = get_connection()
conn.row_factory = sqlite3.Row
rows = conn.execute("""
    SELECT interests.id, interests.name, categories.name AS category_name
    FROM interests
    JOIN categories ON interests.category_id = categories.id
    WHERE interests.category_id = ?;
""", [category_id]).fetchall()
conn.close()
return render(request, "interests/interest_list.html", {"interests": rows})
```
- `sqlite3.Row` позволяет обращаться к полям по именам: `{{ interest.category_name }}` в шаблоне (без него были бы индексы `{{ interest.2 }}`, зависящие от порядка столбцов); имена задаются псевдонимами `AS`;
- значения из адресной строки (`request.GET`) передаются только параметрами `?`, отдельно от текста запроса; конкатенация строк и f-строки для подстановки значений не используются, поэтому запросы вроде `?category=1 OR 1=1` или `?user=1;DROP TABLE users` ничего не находят и ничего не изменяют;
- пустой результат — не ошибка: запрос выполнился, но подходящих записей нет; шаблон показывает сообщение через `{% empty %}` («Интересы не найдены», «Доступных интересов нет»), а для неизвестного пользователя — «Пользователь не найден»;
- в ПР7 страницы интереса `/interests/<id>/` и подписки `/subscriptions/<id>/` работали с JSON; с ПР9 все страницы переведены на Django ORM.

### Что заменил SQL
| Было (Python, ПР3–ПР6) | Стало (SQL, ПР7) |
|---|---|
| связанные объекты (`subscription.user`, `interest.category`) | `JOIN` |
| поиск по номеру в цикле (`find_interest_by_id()`) | `WHERE id = ?` |
| отбор интересов по категории (`filter_interests_by_category()`) | `WHERE category_id = ?` |
| сортировка (`sorted()` с `lambda`) | `ORDER BY` |
| правило `can_subscribe()` для списка интересов | подзапрос `NOT IN` |
| часы по интересам (`get_statistics()`) | `SUM` и `GROUP BY` |

## Модели Django и ORM (ПР9)
В ПР9 слой данных переведён с `sqlite3` на Django ORM. Предметная область, страницы, маршруты и шаблоны сохранены, изменился способ получения данных: вместо SQL-запросов во view используются модели.

Путь данных на веб-страницах: view-функция → Django ORM → SQLite (`db.sqlite3`) → объекты моделей → контекст → шаблон → страница.

| ПР7 (SQL) | ПР9 (ORM) |
|---|---|
| структура таблиц: `sql/schema.sql` | модели в `models.py` приложений |
| изменение структуры: правка схемы вручную | миграции Django |
| подключение: `sqlite3.connect()` | менеджер `objects` модели |
| запросы: `sql/queries.sql` | `filter()`, `exclude()`, `order_by()`, `annotate()`, `aggregate()` |
| связанные данные: `JOIN` | `select_related()`, обратные связи (`related_name`) |
| результат запроса: `sqlite3.Row` | объекты моделей или словари (`values()`) |

### Модели и связи
Пять моделей — по таблицам ПР7. Они не совпадают с классами пакета `models/` (ПР3): это отдельные классы для работы с базой.

| Модель | Файл | Поля | Связи |
|---|---|---|---|
| `Category` | `interests/models.py` | `name` | — |
| `Interest` | `interests/models.py` | `name`, `weekly_goal` (`FloatField`), `is_active` (`BooleanField`, по умолчанию `True`) | `category` → `Category` (`ForeignKey`, `PROTECT`, `related_name="interests"`) |
| `User` | `users/models.py` | `name`, `email` (`EmailField`) | — |
| `Subscription` | `subscriptions/models.py` | `start_date` (`DateField`), `status` (`CharField`, TextChoices) | `user` → `User`, `interest` → `Interest` (`ForeignKey`, `PROTECT`, `related_name="subscriptions"`) |
| `Activity` | `subscriptions/models.py` | `activity_date` (`DateField`), `hours` (`FloatField`) | `subscription` → `Subscription` (`ForeignKey`, `CASCADE`, `related_name="activities"`) |

- первичный ключ `id` Django добавляет сам (`BigAutoField`, настройка `DEFAULT_AUTO_FIELD`);
- `on_delete=PROTECT` запрещает удалять категорию, пользователя и интерес, пока на них ссылаются интересы и подписки: история подписок сохраняется; занятия — часть подписки, поэтому для них `CASCADE`: они удаляются вместе с подпиской;
- `related_name` задаёт обратный доступ: `category.interests.all()`, `interest.subscriptions.all()`, `user.subscriptions.all()`, `subscription.activities.all()`;
- `subscription.user` и `subscription.interest` — связанные объекты, `subscription.user_id` и `subscription.interest_id` — только номера (столбцы внешних ключей в таблице);
- методы моделей: `Interest.can_subscribe(user)` (правило подписки), `Subscription.cancel()`, `Subscription.get_total_hours()` (`aggregate(Sum("hours"))`), `__str__()`;
- класс `Meta`: сортировка по умолчанию (`ordering`) и русские названия (`verbose_name`).

Модель `User` — пользователь предметной области, а не встроенная модель аутентификации Django: вход и регистрация не реализуются. Приложение `users` создано командой `python manage.py startapp users` и записано в `INSTALLED_APPS`.

### Миграции
```text
python manage.py makemigrations interests users subscriptions
python manage.py sqlmigrate subscriptions 0001
python manage.py migrate
python manage.py showmigrations
python manage.py makemigrations --check
```
- `makemigrations` создаёт файлы миграций (`0001_initial.py` в `interests/migrations/`, `users/migrations/`, `subscriptions/migrations/`); сама по себе она базу не меняет;
- `sqlmigrate` показывает SQL миграции, `migrate` применяет её к базе, `showmigrations` отмечает применённые миграции знаком `[X]`;
- `makemigrations --check` сообщает, остались ли изменения моделей без миграции (ожидаемый ответ: `No changes detected`);
- файлы миграций хранятся в Git; таблицы создаются в `db.sqlite3` (настройка `DATABASES` не менялась): `interests_category`, `interests_interest`, `users_user`, `subscriptions_subscription`, `subscriptions_activity`.

### Стратегия перехода и перенос данных
Выбран вариант «таблицы под управлением Django и перенос данных»: исходная база ПР7 `data/interest_tracker.sqlite` не изменяется и служит источником, Django работает с отдельным файлом `db.sqlite3` (в Git не хранится). Применять миграции к самой базе ПР7 нельзя: Django не знает о её таблицах и попытался бы создать их заново. Перед работой сделана резервная копия `data/interest_tracker_backup.sqlite` (исключена из Git правилом в `.gitignore`).
- `db/inspect_source_db.py` только читает исходную базу: таблицы, столбцы, число записей, проверка внешних ключей (`python db/inspect_source_db.py`);
- `db/import_sqlite_to_orm.py` переносит данные через модели в порядке «категории, пользователи, интересы, подписки, занятия»: `update_or_create(pk=...)` сохраняет прежние номера записей (повторный запуск безопасен — записи обновляются, а не дублируются), `transaction.atomic()` откатывает всё при ошибке, строки дат переводятся в `date`, значения 0 и 1 — в `bool` (`python db/import_sqlite_to_orm.py`).

Результат переноса: 5 категорий, 2 пользователя, 6 интересов, 6 подписок, 12 занятий (22,0 ч) — как в ПР7. Порядок на новом компьютере: `python manage.py migrate`, затем `python db/import_sqlite_to_orm.py`.

### ORM-запросы проекта
| № | Что делает | Запрос | Где используется |
|---|---|---|---|
| 1 | набор объектов, сортировка | `Category.objects.order_by("name")` | кнопки категорий на `/interests/` |
| 2 | объект по номеру, 404, связь | `get_object_or_404(Interest.objects.select_related("category"), pk=...)` | `/interests/<id>/` |
| 3 | объект через `get()` | `User.objects.get(pk=...)` и `except User.DoesNotExist` | `/interests/available/` |
| 4 | фильтр по полю связанной модели | `Interest.objects.filter(category__id=...)` | `/interests/?category=` |
| 5 | поиск по нескольким полям | `filter(Q(name__iregex=...) \| Q(category__name__iregex=...))` | `/interests/?q=` |
| 6 | фильтр по нескольким условиям | `self.subscriptions.active().filter(user=user).exists()` | `Interest.can_subscribe()` |
| 7 | исключение записей | `Interest.objects.filter(is_active=True).exclude(pk__in=subscribed_ids)` | `/interests/available/` |
| 8 | номера занятых интересов | `Subscription.objects.active().filter(user=...).values_list("interest_id", flat=True)` | `/interests/available/` |
| 9 | цепочка фильтров | `Subscription.objects.active()`, затем `.filter(start_date=...)`, `.filter(interest__id=...)`, `.filter(user__id=...)` | `/subscriptions/` |
| 10 | сортировка по полю связанной модели | `.order_by(sort_field, "id")`, поле — из словаря `sort_fields` | `/subscriptions/?sort=` |
| 11 | вычисляемые поля, `values()` | `.annotate(user_name=F("user__name"), interest_name=F("interest__name")).values(...)` | `/subscriptions/` |
| 12 | постраничный вывод | `Paginator(subscriptions_data, 3)`, `get_page()` | `/subscriptions/?page=` |
| 13 | подсчёт записей | `Subscription.objects.active().count()` | `/subscriptions/` |
| 14 | связанные объекты одним запросом | `Subscription.objects.select_related("user", "interest__category")` | `/subscriptions/<id>/` |
| 15 | сводные показатели | `Activity.objects.aggregate(Count("id"), Coalesce(Sum("hours"), 0.0))` | `/subscriptions/statistics/` |
| 16 | счёт с условием (`Q`) | `Interest.objects.annotate(Count("subscriptions", filter=Q(subscriptions__status=Subscription.Status.ACTIVE)))` | `/subscriptions/statistics/` |
| 17 | сумма по цепочке связей | `Interest.objects.annotate(Coalesce(Sum("subscriptions__activities__hours"), 0.0))` | `/subscriptions/statistics/` |
| 18 | группировка | `Category.objects.annotate(Count("interests"))` | `/subscriptions/statistics/` |
| 19 | фильтр по агрегату (`HAVING`) | `.filter(interests_count__gt=1)` | `/subscriptions/statistics/` |
| 20 | сумма по обратной связи | `self.activities.aggregate(total=Sum("hours"))` | `Subscription.get_total_hours()` |

Пояснения:
- статистика строится от `Interest` и `Category`, а не от `Subscription`: интересы и категории без связанных записей остаются в результате со счётом 0 (аналог `LEFT JOIN` из ПР7); условие `Q(subscriptions__status=Subscription.Status.ACTIVE)` ограничивает только подсчёт;
- часы по интересам считаются по всем подпискам, включая отменённые, как в консольной статистике: общий итог 22,0 ч;
- `values()` возвращает словари: шаблон списка подписок использует `subscription.user_name`; у объектов моделей (`select_related()`) обращение идёт через связь — в карточке интереса `interest.category_name` заменено на `interest.category.name`;
- значения из адресной строки проверяются: номера — методом `isdecimal()`, дата — `strptime()` (при ошибке выводится «Укажите корректную дату.»), поле сортировки выбирается только из словаря `sort_fields` (неизвестное значение — сортировка по дате), некорректный `?page=` открывает первую страницу (`get_page()`);
- номера проверяются как `category__id`, `interest__id`, `user__id`, а не `category_id`: слишком большое число даёт пустой результат, а не ошибку базы данных;
- SQLite сравнивает без учёта регистра только латиницу (`LIKE`), поэтому `icontains` не находит «бег» в «Бег»; для поиска использован `iregex` с `re.escape()`: он работает и для кириллицы, а спецсимволы в запросе (`.`, `*`) воспринимаются как обычный текст;
- ссылки пагинации и фильтров строятся тегом `{% querystring %}`: он сохраняет остальные параметры запроса (дату, интерес, пользователя, сортировку, поиск);
- пустой результат — не ошибка: шаблоны показывают сообщения через `{% empty %}`.

Операции создания, изменения и удаления проверяются в Django shell (`python manage.py shell`); веб-формы появятся в следующих работах. Пример:
```python
from interests.models import Category, Interest
category = Category.objects.create(name="Тест")
interest = Interest.objects.create(name="Проба", category=category, weekly_goal=1.5)
interest.weekly_goal = 2.0
interest.save()
interest.delete()
category.delete()
```
Удаление `Category`, пока на неё ссылается интерес, вызовет `ProtectedError`.

### Просмотр SQL-запросов: Django Debug Toolbar
В ПР10 настройки панели и актуальные результаты анализа SQL приведены в разделе
«Практическая работа 10» в начале README. Для просмотра включите `DJANGO_DEBUG=1`.
Без отладки панель отключена. Карточка подписки выполняет 3 запроса, список — 6,
включая общий счётчик интересов в навигации.

## Структура проекта
```text
personal_interesting/
├── README.MD
├── requirements.txt
├── pytest.ini
├── .flake8
├── manage.py
├── main.py
├── storage.py
├── utils.py
├── db/
│   ├── __init__.py
│   ├── database.py
│   ├── import_json.py
│   ├── inspect_source_db.py
│   └── import_sqlite_to_orm.py
├── sql/
│   ├── schema.sql
│   └── queries.sql
├── interest_tracker/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── templates/
│   ├── base.html
│   └── includes/
│       └── navigation.html
├── homepage/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   ├── models.py
│   ├── static/
│   │   └── homepage/
│   │       ├── css/
│   │       │   └── style.css
│   │       ├── img/
│   │       │   └── logo.png
│   │       └── js/
│   │           └── main.js
│   ├── templates/
│   │   └── homepage/
│   │       ├── index.html
│   │       └── page_not_found.html
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── interests/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   │   └── 0001_initial.py
│   ├── models.py
│   ├── templates/
│   │   └── interests/
│   │       ├── includes/
│   │       │   └── interest_card.html
│   │       ├── available.html
│   │       ├── interest_detail.html
│   │       └── interest_list.html
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── subscriptions/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   │   └── 0001_initial.py
│   ├── models.py
│   ├── templates/
│   │   └── subscriptions/
│   │       ├── includes/
│   │       │   └── subscription_status.html
│   │       ├── statistics.html
│   │       ├── subscription_detail.html
│   │       └── subscription_list.html
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── users/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   │   └── 0001_initial.py
│   ├── models.py
│   └── tests.py
├── models/
│   ├── __init__.py
│   ├── categories.py
│   ├── interests.py
│   ├── users.py
│   └── subscriptions.py
├── data/
│   ├── categories.json
│   ├── interests.json
│   ├── users.json
│   ├── subscriptions.json
│   └── interest_tracker.sqlite
└── tests/
    ├── test_interests.py
    ├── test_users.py
    ├── test_subscriptions.py
    └── test_storage.py
```
Файл `db.sqlite3` появляется после команды `python manage.py migrate` (таблицы проекта и служебные таблицы Django), данные в него переносит `db/import_sqlite_to_orm.py`; в Git он не хранится. Файл `data/interest_tracker.sqlite` — база данных ПР7: в Git хранится, после ПР9 служит источником данных для переноса.

## Назначение модулей
- `main.py` — консольная версия приложения (сохранена с ПР3): меню, ввод данных и пользовательские сценарии (подписка, отметка занятия, прогресс, добавление интереса). Загружает и сохраняет данные через `storage.py` и не хранит данные в словарях;
- `manage.py` — запуск команд управления Django-проектом (`runserver`, `migrate`, `check`);
- `interest_tracker/` — пакет настроек Django-проекта: `settings.py` — настройки (в том числе список приложений `INSTALLED_APPS`, каталог шаблонов `TEMPLATES`, язык и часовой пояс, `DEBUG` и `ALLOWED_HOSTS`), `urls.py` — маршрутизация верхнего уровня и `handler404`, `asgi.py` и `wsgi.py` — точки входа для серверов;
- `templates/` — шаблоны уровня проекта: `base.html` (базовый шаблон всех страниц) и `includes/navigation.html` (навигация);
- `homepage/` — Django-приложение главной страницы: `views.py` — view-функция `index()` и обработчик ошибки 404 `page_not_found()`; `urls.py` — маршрут главной страницы; `templates/homepage/` — шаблоны главной страницы и страницы «Страница не найдена»; `static/homepage/` — собственные CSS, JavaScript и логотип проекта (общие для всех страниц);
- `interests/` — Django-приложение интересов: `models.py` — модели `Category` и `Interest`, `migrations/` — миграции, `views.py` — view-функции `interests()`, `available_interests()` и `interest_detail()` (запросы через ORM), `urls.py` — маршруты приложения, `templates/interests/` — шаблоны списка, поиска доступных интересов, страницы и карточки интереса;
- `subscriptions/` — Django-приложение подписок: `models.py` — модели `Subscription` и `Activity`, `migrations/` — миграции, `views.py` — view-функции `subscriptions()`, `statistics()` и `subscription_detail()` (запросы через ORM), `urls.py` — маршруты приложения, `templates/subscriptions/` — шаблоны списка, статистики, страницы и статуса подписки;
- `users/` — Django-приложение пользователей: `models.py` — модель `User` (пользователь предметной области), `migrations/` — миграции;
- `db/` — работа с базой данных: `database.py` и `import_json.py` — подключение к SQLite и перенос данных из JSON (ПР7, `python -m db.import_json`), `inspect_source_db.py` и `import_sqlite_to_orm.py` — просмотр исходной базы и перенос её данных в модели Django (ПР9);
- `sql/` — SQL-файлы (ПР7): `schema.sql` — создание таблиц, `queries.sql` — запросы проекта с комментариями;
- `models/__init__.py` — позволяет импортировать классы из пакета: `from models import Category, Interest, Subscription, User`;
- `models/categories.py` — класс `Category` и функции работы с категориями;
- `models/interests.py` — класс `Interest` и функции работы с интересами (добавление, поиск, отбор по категории, сортировка);
- `models/users.py` — класс `User` и функции работы с пользователями;
- `models/subscriptions.py` — класс `Subscription`, функции оформления и отмены подписок, прогресс, рекомендации и статистика;
- `storage.py` — загрузка и сохранение данных: JSON → объекты Python и объекты Python → JSON;
- `utils.py` — безопасный ввод чисел и дат, форматирование даты, следующий номер записи;
- `tests/` — автоматизированные тесты pytest;
- `pytest.ini` и `.flake8` — настройки запуска тестов и линтера.

## Функции проекта
Функции сущностей и хранилища используются и консольной, и веб-версией. Веб-слой (ПР5, ПР6) вызывает функции загрузки данных, поиска по номеру и проверки правил подписки вместо консольных сценариев `main.py`.

Категория (`models/categories.py`):

| Имя | Назначение |
|---|---|
| `Category` (класс) | категория: атрибуты `id`, `name` |
| `add_category()` | создание категории и добавление её в список |
| `find_category_by_id()` | поиск категории по номеру |
| `show_categories()` | вывод категорий в консоль |

Интерес (`models/interests.py`):

| Имя | Назначение |
|---|---|
| `Interest` (класс) | интерес: атрибуты `id`, `name`, `category`, `weekly_goal`, `is_active` |
| `validate_weekly_goal()` (`@staticmethod`) | проверка недельной цели: больше 0 и не больше 168 ч |
| `add_interest()` | создание интереса и добавление его в список |
| `find_interests()` | поиск интересов по части названия |
| `filter_interests_by_category()` | отбор интересов по категории |
| `sort_interests()` | сортировка интересов по недельной цели |
| `find_interest_by_id()` | поиск интереса по номеру; используется страницей интереса |
| `show_interests()` | вывод интересов в консоль |

Пользователь (`models/users.py`):

| Имя | Назначение |
|---|---|
| `User` (класс) | пользователь: атрибуты `id`, `name`, `email` |
| `from_data()` (`@classmethod`) | создание пользователя из словаря JSON |
| `add_user()` | создание пользователя и добавление его в список |
| `find_user()` | поиск пользователей по имени или почте |
| `find_user_by_id()` | поиск пользователя по номеру |
| `show_users()` | вывод пользователей в консоль |

Подписка (`models/subscriptions.py`):

| Имя | Назначение |
|---|---|
| `Subscription` (класс) | подписка: атрибуты `id`, `user`, `interest`, `start_date`, `is_cancelled`, `hours_by_date` |
| `status` (`@property`) | состояние текстом: «активна» или «отменена»; используется страницами подписок |
| `cancel()` | отмена подписки |
| `add_activity()` | отметка занятия: дата и часы |
| `get_weekly_hours()` | часы за неделю |
| `get_total_hours()` | все часы по подписке; используется страницей подписки |
| `can_subscribe()` | проверка правил подписки; используется страницей интереса |
| `create_subscription()` | проверка правил, создание подписки и добавление её в список |
| `cancel_subscription()` | поиск подписки и вызов её метода `cancel()` |
| `get_subscription_status()` | сообщение о том, можно ли оформить подписку |
| `find_subscription_by_id()` | поиск подписки по номеру; используется страницей подписки |
| `show_subscriptions()` | вывод подписок в консоль |
| `calculate_progress()`, `generate_recommendation()`, `display_interest_card()` | прогресс за неделю, рекомендация и карточка интереса (функции ПР1) |
| `get_statistics()`, `show_statistics()` | часы по каждому интересу |

Хранение данных (`storage.py`):

| Имя | Назначение |
|---|---|
| `load_categories()`, `save_categories()` | `data/categories.json`: JSON ↔ объекты `Category` |
| `load_interests()`, `save_interests()` | `data/interests.json`: JSON ↔ объекты `Interest` |
| `load_users()`, `save_users()` | `data/users.json`: JSON ↔ объекты `User` |
| `load_subscriptions()`, `save_subscriptions()` | `data/subscriptions.json`: JSON ↔ объекты `Subscription` |

База данных (ПР7):

| Имя | Файл | Назначение |
|---|---|---|
| `get_connection()` | `db/database.py` | подключение к `data/interest_tracker.sqlite` с включённой проверкой внешних ключей |
| `load_json()` | `db/import_json.py` | чтение списка записей из JSON-файла |
| `import_categories()`, `import_users()`, `import_interests()`, `import_subscriptions()`, `import_activities()` | `db/import_json.py` | перенос данных одной таблицы из JSON в SQLite (`executemany()` с параметрами `?`) |
| `main()` | `db/import_json.py` | импорт всех таблиц в одной транзакции с `commit()` и `rollback()` |

Перенос в ORM (ПР9):

| Имя | Файл | Назначение |
|---|---|---|
| (скрипт) | `db/inspect_source_db.py` | чтение исходной базы: таблицы, столбцы, число записей, проверка внешних ключей |
| `read_source()` | `db/import_sqlite_to_orm.py` | чтение таблиц исходной базы ПР7 (только чтение) |
| `main()` | `db/import_sqlite_to_orm.py` | перенос данных в модели Django: `update_or_create(pk=...)` в одной транзакции `transaction.atomic()` |

Модели Django (ПР9):

| Имя | Файл | Назначение |
|---|---|---|
| `Interest.can_subscribe()` | `interests/models.py` | правило подписки через ORM: интерес активен и у пользователя нет его активной подписки; используется страницей интереса |
| `Subscription.cancel()` | `subscriptions/models.py` | отмена подписки: `save(update_fields=["status"])` |
| `Subscription.get_total_hours()` | `subscriptions/models.py` | сумма часов занятий: `aggregate(Sum("hours"))`; используется страницей подписки |

Веб-слой (ПР5–ПР9): каждая view-функция готовит контекст и вызывает `render()`, HTML формирует шаблон. Данные view получает через ORM.

| Имя | Файл | Шаблон | Назначение |
|---|---|---|---|
| `index()` | `homepage/views.py` | `homepage/index.html` | главная страница `/` |
| `page_not_found()` | `homepage/views.py` | `homepage/page_not_found.html` | обработчик `handler404`: страница «Страница не найдена» с кодом 404 |
| `interests()` | `interests/views.py` | `interests/interest_list.html` | страница `/interests/`: список интересов, фильтр по категории и поиск |
| `available_interests()` | `interests/views.py` | `interests/available.html` | страница `/interests/available/`: интересы, доступные выбранному пользователю |
| `interest_detail()` | `interests/views.py` | `interests/interest_detail.html` | страница `/interests/<int:interest_id>/`; если интереса нет — 404 |
| `subscriptions()` | `subscriptions/views.py` | `subscriptions/subscription_list.html` | страница `/subscriptions/`: активные подписки, фильтры, сортировка, пагинация |
| `statistics()` | `subscriptions/views.py` | `subscriptions/statistics.html` | страница `/subscriptions/statistics/`: статистика |
| `subscription_detail()` | `subscriptions/views.py` | `subscriptions/subscription_detail.html` | страница `/subscriptions/<int:subscription_id>/`; если подписки нет — 404 |

## Требования
- Python 3.10 или новее;
- Django 5.2;
- django-debug-toolbar;
- pytest;
- flake8.

Консольная версия использует только стандартную библиотеку, веб-версии нужен Django. Установка зависимостей (в виртуальное окружение):
```text
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Запуск программы
Веб-версия (Django). Данные хранит база Django `db.sqlite3`; в Git она не хранится, поэтому после клонирования репозитория нужно создать таблицы и перенести в них данные из `data/interest_tracker.sqlite`:
```text
python manage.py migrate
python db/import_sqlite_to_orm.py
python manage.py runserver --insecure
```
Команды `migrate` и `python db/import_sqlite_to_orm.py` выполняются один раз: первая применяет миграции Django и проекта и создаёт таблицы в `db.sqlite3`, вторая переносит данные (повторный запуск безопасен: записи обновляются, а не дублируются). Флаг `--insecure` нужен, потому что в настройках `DEBUG = False`, а при таком значении сервер разработки не раздаёт статические файлы (CSS, JavaScript, логотип); без флага страницы откроются без оформления проекта. После запуска сервера открыть в браузере адрес:
```text
http://127.0.0.1:8000/
```

Системная проверка проекта Django и состояние миграций:
```text
python manage.py check
python manage.py showmigrations
python manage.py makemigrations --check
```

Проверка, что Django находит статические файлы проекта:
```text
python manage.py findstatic homepage/img/logo.png
```

Консольная версия (сохранена):
```text
python main.py
```

Меню консольной версии:
```text
=== Система управления личными интересами ===
Подписки:
 1. Подписаться на интерес
 2. Отменить подписку
 3. Показать подписки
 4. Отметить занятие по подписке
 5. Прогресс по подписке за неделю
 6. Статистика по интересам
Интересы и категории:
 7. Показать интересы
 8. Найти интерес по названию
 9. Отсортировать интересы по недельной цели
10. Показать интересы категории
11. Добавить интерес
12. Добавить категорию
Пользователи:
13. Показать пользователей
14. Найти пользователя
15. Добавить пользователя
 0. Выход
```

В каталоге `data/` лежат подготовленные данные: 5 категорий, 6 интересов (один в архиве), 2 пользователя и 6 подписок (две отменены) с занятиями за две недели (07.09–13.09.2026 и 14.09–20.09.2026). Даты в консольной версии вводятся в формате `ДД.ММ.ГГГГ`.

Что можно проверить на подготовленных данных в консоли:
- пункт 1, пользователь 1, интерес 1 — отказ: Иван Петров уже подписан;
- пункт 1, любой пользователь, интерес 5 — отказ: интерес в архиве;
- пункт 1, пользователь 2, интерес 2 — подписка оформится: прежняя подписка Анны на «Бег» отменена;
- пункт 5, подписка 1, дата `16.09.2026` — карточка прогресса:
```text
=======================================================
КАРТОЧКА ИНТЕРЕСА: ИЗУЧЕНИЕ ВЕБ-РАЗРАБОТКИ НА PYTHON
=======================================================
Пользователь:       Иван Петров
Категория:          Программирование
Дата подписки:      08.09.2026
Статус подписки:    активна
План на неделю:     8.0 ч.
Затрачено:          9.0 ч.
Прогресс:           112.5%
-------------------------------------------------------
Рекомендация:       Отличный результат! Недельная цель полностью выполнена.
=======================================================
```

Что можно проверить в браузере на подготовленных данных:
- `/` — главная: логотип, навигация, кнопки разделов, в подвале «© 2026 Interest Tracker» (год подставляет `main.js`);
- `/interests/` — «Всего интересов: 6», поле поиска, кнопки-фильтры категорий, карточки интересов из базы (ORM), у каждой кнопка «Подробнее»;
- `/interests/?category=2` — только интересы категории «Спорт» (Бег, Стрельба из лука), «Всего интересов: 2»;
- `/interests/?q=бег` — только «Бег» (регистр не важен); `?q=спорт` — оба интереса категории «Спорт» (поиск идёт по названию интереса и по названию категории); `?q=zzz` — «Интересы не найдены.»;
- `/interests/available/` — форма выбора пользователя; для Ивана Петрова (`?user=1`) — «Английский язык», «Бег», «Гитара», для Анны Смирновой (`?user=2`) — «Бег», «Изучение веб-разработки на Python», «Стрельба из лука»; для несуществующего пользователя (`?user=999`) — «Пользователь не найден»;
- `/subscriptions/statistics/` — «Отмечено занятий: 12, всего часов: 22,0», таблицы подписок и часов по интересам, интересов по категориям, список «Спорт: 2»;
- `/interests/1/` — Иван Петров: «подписка невозможна» (уже подписан), Анна Смирнова: «можно подписаться»;
- `/interests/2/` — «Бег»: оба пользователя могут подписаться, прежние подписки отменены;
- `/interests/5/` — интерес в архиве: подписка невозможна для всех;
- `/subscriptions/` — «Активных подписок: 4, найдено по условиям: 4», по 3 подписки на странице (№1, 3, 4 на первой, №6 на второй) и навигация по страницам; отменённые (№2, 5) в список не входят; фильтры (`?user=2` — две подписки Анны, `?interest=1`, `?date=2026-09-10`) и сортировка (`?sort=user`, `?sort=interest`) сохраняются при переходе между страницами; `?date=не-дата` — сообщение «Укажите корректную дату.», `?page=abc` — первая страница;
- `/subscriptions/1/` — активная подписка, отмечено 13,0 ч;
- `/subscriptions/2/` — отменённая подписка, статус «отменена»;
- `/interests/999/` и `/subscriptions/999/` — страница «Страница не найдена» и код статуса 404 (`get_object_or_404()` вызывает `Http404`, ответ формирует `handler404`);
- `/abc/` или `/interests/abc/` — страница «Страница не найдена» и код статуса 404 (формирует `handler404`).

## Тестирование
```text
pytest -v
```

Тесты ПР3 проходят без изменений: консольная часть проекта сохранена. Они проверяют:
- создание объектов `Interest`, `User`, `Subscription`, их атрибуты и строковое представление;
- методы классов: `validate_weekly_goal()`, `from_data()`, `cancel()`, `add_activity()`, `get_weekly_hours()`;
- добавление, поиск и отбор интересов по категории;
- связь подписки с пользователем и интересом;
- правила подписки: нельзя подписаться дважды и на интерес в архиве, после отмены подписаться снова можно;
- функции ПР1: расчёт прогресса и рекомендацию;
- сохранение подписок в JSON и восстановление связей с объектами при загрузке.

Веб-слой проверяется 22 тестами `subscriptions/tests.py` через `python manage.py test`. Консольные классы проверяются отдельно: `pytest -v`, 17 тестов. Протоколы ПР10 находятся в `docs/pr10/`.

## Проверка качества кода
```text
flake8
```
Если замечаний нет, flake8 ничего не выводит. Каталог `.venv` исключён из проверки. Для сгенерированных Django файлов `manage.py`, `interest_tracker/settings.py` и файлов миграций (`*/migrations/*.py`) в `.flake8` отключена только проверка длины строки (E501): в них есть длинные строки с путями к классам Django.

## Git
Исходный код хранится в Git-репозитории: https://github.com/Mikle-kekich/Personal-Interes

Проверка состояния репозитория:
```text
git status
```
Коммиты ПР5 начинаются с метки `PR5:`, коммиты ПР6 — с метки `PR6:`, коммиты ПР7 — с метки `PR7:`, коммиты ПР9 — с метки `PR9:` (например, `PR9: переход на Django ORM`). Файлы миграций хранятся в Git, локальная база `db.sqlite3` и резервная копия `data/interest_tracker_backup.sqlite` — нет.

## Текущее состояние и план развития
### Этап ПР9 до настройки административной панели
На ПР9 слой данных переведён на Django ORM:
- описаны модели `Category`, `Interest`, `User`, `Subscription` и `Activity`, связи `ForeignKey` с `on_delete` и `related_name`; создано приложение `users`;
- созданы и применены миграции (`makemigrations`, `migrate`), структура базы управляется миграциями;
- данные из базы ПР7 перенесены в базу Django скриптом `db/import_sqlite_to_orm.py` с сохранением номеров записей и связей (5 категорий, 2 пользователя, 6 интересов, 6 подписок, 12 занятий);
- все страницы получают данные через ORM: фильтрация, `exclude()`, поиск, сортировка по разрешённым полям, `select_related()`, `aggregate()`, `annotate()` и `Count` с `Q`, `Paginator` с сохранением параметров запроса (`{% querystring %}`);
- некорректные параметры (дата, номера, сортировка, страница) и отсутствующие объекты обрабатываются без ошибок;
- из представлений удалены `sqlite3` и `load_data()`; SQL-слой ПР7 (`sql/`, `db/database.py`, `db/import_json.py`) оставлен как предыдущая реализация;
- подключена панель Django Debug Toolbar: вкладка «SQL» показывает запросы каждой страницы;
- консольная версия, JSON-хранилище, шаблоны, маршруты и все 17 тестов сохранены.

Реализовано (ПР7):
На ПР7 данные проекта перенесены из JSON в базу данных SQLite:
- создана база данных `data/interest_tracker.sqlite`, таблицы созданы командами из `sql/schema.sql` (пять таблиц, первичные и внешние ключи);
- данные перенесены из JSON скриптом `db/import_json.py`, подключение к базе — `db/database.py` (`PRAGMA foreign_keys = ON`);
- 15 SQL-запросов сохранены в `sql/queries.sql`: списки, `WHERE`, `JOIN`, `COUNT` и `SUM`, `GROUP BY`, `HAVING`, подзапрос `NOT IN`;
- Django-представления получают данные из SQLite через `sqlite3` (`row_factory = sqlite3.Row`, параметризованные запросы с `?`) и передают их в шаблоны через контекст;
- страницы списка интересов (с фильтром по категории), активных подписок, поиска доступных интересов и статистики работают с базой данных, в навигацию добавлен раздел «Статистика»;
- консольная версия, JSON-хранилище, страницы интереса и подписки (ПР5–ПР6) и все 17 тестов сохранены.

Реализовано (ПР6):
- шаблоны Django: базовый шаблон `base.html`, наследование `{% extends %}` и блоки `{% block %}`;
- включаемые шаблоны `{% include %}`: навигация, карточка интереса, статус подписки;
- передача данных из view в шаблон через контекст и `render()`; циклы `{% for %}` с `{% empty %}` и условия `{% if %}`;
- именованные URL и пространства имён (`app_name`), ссылки через `{% url %}`;
- фильтры шаблонов `length`, `default`, `floatformat`;
- статические файлы: собственные CSS, JavaScript и логотип, подключение через `{% load static %}` и `{% static %}`;
- функция `page()` удалена: HTML-код в view-функциях больше не формируется.

Реализовано (ПР5):
- Django-проект `interest_tracker` и три Django-приложения (`homepage`, `interests`, `subscriptions`);
- маршрутизация URL двух уровней: корневой `urls.py` и `urls.py` каждого приложения;
- view-функции и пять страниц: главная, список и страница интереса, список и страница подписки;
- динамические URL с конвертером `<int:...>` и ответ с кодом 404 для несуществующего номера;
- обработка ошибки 404 для несуществующих адресов: `handler404` и страница «Страница не найдена», заданы `DEBUG = False` и `ALLOWED_HOSTS`;
- отображение данных предметной области из JSON через классы и функции ПР3;
- проверка правил подписки (`can_subscribe()`) на странице интереса;
- навигация между страницами и оформление Bootstrap 5.3.

В ПР10 редактирование данных и аутентификация сотрудников доступны через Django Admin. Публичные формы подписки и пользовательская регистрация пока не реализованы.

Планируется:
- подключение PostgreSQL вместо SQLite (настройка `DATABASES`, перенос данных);
- формы и POST-запросы: оформление и отмена подписки, отметка занятий, добавление интересов и категорий, использование отложенной логики ПР3;
- аутентификация, регистрация и разграничение прав доступа пользователей;
- REST API для интеграции с мобильными или внешними клиентами;
- расширение покрытия бизнес-логики и будущих публичных форм;
- контейнеризация приложения с использованием Docker и Docker Compose;
- настройка базового CI/CD пайплайна для автоматической проверки и развёртывания.
