# Система управления личными интересами (Interest Tracker)

Приложение, в котором пользователи подписываются на интересы (хобби) из разных категорий, отмечают занятия по подписке и следят за выполнением недельного плана. Консольная версия (ПР3) дополнена веб-интерфейсом на Django (ПР5): интересы и подписки можно просматривать в браузере. Страницы веб-интерфейса формируются шаблонами Django (ПР6). Данные списка интересов, активных подписок, поиска доступных интересов и статистики берутся из базы данных SQLite с помощью SQL-запросов (ПР7).

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
- SQLite и язык SQL — реляционная база данных проекта, работа с ней через модуль `sqlite3` стандартной библиотеки Python (без Django ORM);
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
Пользователь, интерес, категория, подписка. Каждая сущность — отдельный класс в своём файле пакета `models/`.

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

Django-проект `interest_tracker` создан в корне существующего репозитория, рядом с кодом ПР1–ПР3. Он состоит из трёх Django-приложений:
- `homepage` — главная страница и общий каркас всех страниц;
- `interests` — страницы интересов (категория показывается в интересе как его атрибут);
- `subscriptions` — страницы подписок.

Отдельное приложение для пользователей не создаётся: у Django есть встроенная модель пользователя (`django.contrib.auth`), работа с пользователями (регистрация, вход, разграничение доступа) будет рассмотрена в следующих темах. Пользователи ПР3 (класс `User`) по-прежнему загружаются из `data/users.json` и показываются на страницах интересов и подписок.

Не следует путать пакет `models/` (классы предметной области ПР3) и файлы `models.py` Django-приложений: последние пока пустые, Django-модели появятся на следующих работах.

## Страницы веб-интерфейса
- `/` — главная страница: описание приложения и кнопки-ссылки на разделы (view-функция `index()`);
- `/interests/` — список интересов **из базы SQLite** (запрос с JOIN): категория, план на неделю, статус; ссылки-фильтры по категориям (`?category=<номер>`, запрос с параметром) (view-функция `interests()`);
- `/interests/available/` — **поиск доступных интересов** (ПР7): по выбранному пользователю (`?user=<номер>`) показываются активные интересы, на которые у него нет действующей подписки (подзапрос `NOT IN`, параметр `?`) (view-функция `available_interests()`);
- `/interests/<int:interest_id>/` — страница интереса: категория, план, статус и проверка `can_subscribe()` для каждого пользователя; данные из JSON (view-функция `interest_detail()`);
- `/subscriptions/` — активные подписки **из базы SQLite** (JOIN трёх таблиц, `WHERE is_cancelled = 0`) и их количество (`COUNT`): пользователь, интерес, дата, статус (view-функция `subscriptions()`);
- `/subscriptions/statistics/` — **статистика** (ПР7): занятия и часы, активные подписки и часы по интересам, интересы по категориям, категории с несколькими интересами (`COUNT`, `SUM`, `GROUP BY`, `HAVING`) (view-функция `statistics()`);
- `/subscriptions/<int:subscription_id>/` — страница подписки: связанные пользователь, интерес и категория, дата, всего часов, статус; данные из JSON (view-функция `subscription_detail()`).

Если интерес или подписка с указанным номером не найдены, страница возвращает сообщение и код статуса 404; адрес, которого нет среди маршрутов, обрабатывает `handler404` (см. ниже). Ссылки навигации («Главная», «Интересы», «Подписки», «Статистика») есть на каждой странице, из списков можно перейти к карточкам, из карточки подписки — к карточке интереса. Номера записей в базе совпадают с номерами в JSON, поэтому ссылки из списков на страницы интереса и подписки ведут на те же записи. Подробнее о базе данных — в разделе «База данных SQLite (ПР7)».

Как запрос доходит до страницы (на примере `/interests/1/`):
```text
браузер: GET /interests/1/
→ interest_tracker/urls.py: path("interests/", include("interests.urls"))
→ interests/urls.py: path("<int:interest_id>/", views.interest_detail, name="detail")
→ interest_detail(request, interest_id=1): загрузка данных, find_interest_by_id(), can_subscribe(), подготовка контекста
→ render(): шаблон interests/interest_detail.html, который наследует templates/base.html
→ HttpResponse: HTML-страница и код статуса 200
```

HTML веб-страниц находится в шаблонах Django (см. раздел «Шаблоны Django (ПР6)»); view-функции HTML не формируют. Функция `page()` из ПР5 удалена.

### Обработка ошибки 404, DEBUG и ALLOWED_HOSTS
В `interest_tracker/settings.py` заданы `DEBUG = False` и `ALLOWED_HOSTS = ['127.0.0.1', 'localhost']`, в `interest_tracker/urls.py` — `handler404 = 'homepage.views.page_not_found'`.
- Адрес не подошёл ни под один маршрут (`/abc/`, `/interests/abc/`): Django получает `Resolver404` и вызывает обработчик `handler404` — функцию `page_not_found(request, exception)` (`homepage/views.py`). Она отображает шаблон `homepage/page_not_found.html` («Страница не найдена») с кодом 404. Без `handler404` Django использовал бы стандартный `django.views.defaults.page_not_found` с простой страницей «Not Found».
- Маршрут найден, но объекта нет (`/interests/999/`): исключения нет, шаблон интереса (или подписки) показывает сообщение «Интерес не найден» («Подписка не найдена»), а view передаёт в `render()` код `status=404`; `handler404` не вызывается.
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
context = {"interests": load_data()["interests"]}
return render(request, "interests/interest_list.html", context)
```
В шаблоне имена ключей контекста становятся переменными: `{% for interest in interests %}`, `{{ interest.name }}`, `{{ interest.category.name }}`. Для пустой коллекции используется `{% empty %}` («Интересы не найдены.», «Подписки не найдены.»). Условия `{% if %}` выбирают вид страницы и значков: интерес активен или в архиве, подписка активна или отменена (`subscription.is_cancelled`), можно или нельзя подписаться (`item.allowed`), найден ли объект. Проверка `can_subscribe()` вызывается во view (шаблон не вычисляет правила), результат передаётся в контексте списком `users_info`.

Если объект не найден, view передаёт `None`, шаблон показывает сообщение через `{% if interest %} ... {% else %} ... {% endif %}`, а код 404 задаётся параметром `status=404 if interest is None else 200` вызова `render()`.

### Фильтры шаблонов
- `{{ interests|length }}` и `{{ subscriptions|length }}` — количество элементов («Всего интересов: 6»);
- `{{ interest.name|default:"Без названия" }}` — значение по умолчанию для пустого названия;
- `{{ interest.weekly_goal|floatformat:1 }}` — число с одним знаком после запятой («8,0 ч»; запятая — из настройки `LANGUAGE_CODE = 'ru-RU'`).

Фильтры используются только для представления данных, бизнес-логика остаётся в Python. Даты подписок хранятся в JSON и в объектах строкой `ГГГГ-ММ-ДД` и выводятся без преобразования (фильтр `date` работает только с объектами даты; они появятся при переходе на Django ORM). В консольной версии дата по-прежнему показывается как `ДД.ММ.ГГГГ`.

### Именованные URL и пространства имён
В `urls.py` каждого приложения задан `app_name` и имена маршрутов; ссылки в шаблонах строятся тегом `{% url %}`, адреса в HTML не записаны:

| Имя маршрута | Адрес | Пример в шаблоне |
|---|---|---|
| `homepage:index` | `/` | `{% url 'homepage:index' %}` |
| `interests:list` | `/interests/` | `{% url 'interests:list' %}` |
| `interests:detail` | `/interests/<int:interest_id>/` | `{% url 'interests:detail' interest.id %}` |
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
### Используется в веб-интерфейсе (ПР5, ПР6, ПР7)
- просмотр списка интересов и отбор по категории (SQLite);
- поиск интересов, доступных для подписки пользователю (SQLite);
- просмотр страницы интереса и проверка правил подписки для каждого пользователя (JSON);
- просмотр активных подписок и их количества (SQLite);
- просмотр страницы подписки со связанными объектами (JSON);
- статистика: занятия, часы по интересам, подписки и интересы по категориям (SQLite).

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
- поиск и сортировка интересов;
- добавление интереса, категории и пользователя, поиск пользователя.

## Хранение данных
Данные хранятся в JSON-файлах каталога `data/`: `categories.json`, `interests.json`, `users.json`, `subscriptions.json`. Даты записаны строкой `ГГГГ-ММ-ДД`. С ПР7 те же данные перенесены в базу SQLite `data/interest_tracker.sqlite` (см. раздел «База данных SQLite (ПР7)»): страницы списка интересов, подписок, поиска и статистики читают базу, консольная версия и карточки интереса и подписки — JSON.

При загрузке (`storage.py`) данные JSON преобразуются в объекты `Category`, `Interest`, `User` и `Subscription`, при сохранении — обратно в словари. Вместо связанных объектов в JSON записываются их номера: `category_id`, `user_id`, `interest_id`. При загрузке по номерам находятся объекты из уже загруженных списков; запись со ссылкой на несуществующий объект пропускается. Если файла нет, программа начинает с пустых данных; если файл повреждён, выводится сообщение и данные из него не загружаются. Данные сохраняются после каждого изменения.

Страницы интереса и подписки только читают JSON: функция `load_data()` (`homepage/views.py`) вызывает функции загрузки из `storage.py` и возвращает словарь со списками объектов. Путь к каталогу `data/` строится от `BASE_DIR` из `settings.py`, поэтому не зависит от текущего каталога.

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
В ПР7 проект получил слой реляционного хранения данных: файл базы `data/interest_tracker.sqlite`, SQL-запросы и их использование в Django-представлениях. Работа идёт напрямую через SQL и модуль `sqlite3` стандартной библиотеки Python, Django ORM пока не используется (служебный файл `db.sqlite3` Django — отдельная база, к данным проекта не относится). JSON-файлы остаются в проекте: из них данные один раз переносятся в базу, а консольная версия (`main.py`) продолжает работать с ними.

Путь данных на веб-страницах: SQLite → SQL-запрос → `sqlite3` во view-функции → контекст → шаблон → страница.

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
- страницы интереса `/interests/<id>/` и подписки `/subscriptions/<id>/` пока работают с JSON (с ПР5): их перевод на базу — в следующих работах.

### Что заменил SQL
| Было (Python, ПР3–ПР6) | Стало (SQL, ПР7) |
|---|---|
| связанные объекты (`subscription.user`, `interest.category`) | `JOIN` |
| поиск по номеру в цикле (`find_interest_by_id()`) | `WHERE id = ?` |
| отбор интересов по категории (`filter_interests_by_category()`) | `WHERE category_id = ?` |
| сортировка (`sorted()` с `lambda`) | `ORDER BY` |
| правило `can_subscribe()` для списка интересов | подзапрос `NOT IN` |
| часы по интересам (`get_statistics()`) | `SUM` и `GROUP BY` |

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
│   └── import_json.py
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
Файл `db.sqlite3` появляется после команды `python manage.py migrate` (служебные таблицы Django) и не хранится в Git. Файл `data/interest_tracker.sqlite` — база данных проекта (ПР7), в отличие от `db.sqlite3` хранится в Git.

## Назначение модулей
- `main.py` — консольная версия приложения (сохранена с ПР3): меню, ввод данных и пользовательские сценарии (подписка, отметка занятия, прогресс, добавление интереса). Загружает и сохраняет данные через `storage.py` и не хранит данные в словарях;
- `manage.py` — запуск команд управления Django-проектом (`runserver`, `migrate`, `check`);
- `interest_tracker/` — пакет настроек Django-проекта: `settings.py` — настройки (в том числе список приложений `INSTALLED_APPS`, каталог шаблонов `TEMPLATES`, язык и часовой пояс, `DEBUG` и `ALLOWED_HOSTS`), `urls.py` — маршрутизация верхнего уровня и `handler404`, `asgi.py` и `wsgi.py` — точки входа для серверов;
- `templates/` — шаблоны уровня проекта: `base.html` (базовый шаблон всех страниц) и `includes/navigation.html` (навигация);
- `homepage/` — Django-приложение главной страницы: `views.py` — функция `load_data()` (загрузка данных, её используют остальные приложения), view-функция `index()` и обработчик ошибки 404 `page_not_found()`; `urls.py` — маршрут главной страницы; `templates/homepage/` — шаблоны главной страницы и страницы «Страница не найдена»; `static/homepage/` — собственные CSS, JavaScript и логотип проекта (общие для всех страниц);
- `interests/` — Django-приложение интересов: `views.py` — view-функции `interests()` и `available_interests()` (SQL-запросы к SQLite) и `interest_detail()` (JSON), `urls.py` — маршруты приложения, `templates/interests/` — шаблоны списка, поиска доступных интересов, страницы и карточки интереса, `models.py` — Django-модели (заполняется в следующих работах);
- `subscriptions/` — Django-приложение подписок: `views.py` — view-функции `subscriptions()` и `statistics()` (SQL-запросы к SQLite) и `subscription_detail()` (JSON), `urls.py` — маршруты приложения, `templates/subscriptions/` — шаблоны списка, статистики, страницы и статуса подписки, `models.py` — Django-модели (заполняется в следующих работах);
- `db/` — слой базы данных (ПР7): `database.py` — подключение к SQLite (`get_connection()`), `import_json.py` — перенос данных из JSON в базу (`python -m db.import_json`);
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

Веб-слой (ПР5–ПР7): каждая view-функция готовит контекст и вызывает `render()`, HTML формирует шаблон.

| Имя | Файл | Шаблон | Назначение |
|---|---|---|---|
| `load_data()` | `homepage/views.py` | — | загрузка всех данных проекта из JSON через функции `storage.py` |
| `index()` | `homepage/views.py` | `homepage/index.html` | главная страница `/` |
| `page_not_found()` | `homepage/views.py` | `homepage/page_not_found.html` | обработчик `handler404`: страница «Страница не найдена» с кодом 404 для адресов вне маршрутов |
| `interests()` | `interests/views.py` | `interests/interest_list.html` | страница `/interests/`: список интересов и фильтр по категории (SQLite) |
| `available_interests()` | `interests/views.py` | `interests/available.html` | страница `/interests/available/`: интересы, доступные выбранному пользователю (SQLite) |
| `interest_detail()` | `interests/views.py` | `interests/interest_detail.html` | страница `/interests/<int:interest_id>/` (JSON); если интереса нет — код 404 |
| `subscriptions()` | `subscriptions/views.py` | `subscriptions/subscription_list.html` | страница `/subscriptions/`: активные подписки и их количество (SQLite) |
| `statistics()` | `subscriptions/views.py` | `subscriptions/statistics.html` | страница `/subscriptions/statistics/`: статистика (SQLite) |
| `subscription_detail()` | `subscriptions/views.py` | `subscriptions/subscription_detail.html` | страница `/subscriptions/<int:subscription_id>/` (JSON); если подписки нет — код 404 |

## Требования
- Python 3.10 или новее;
- Django 5.2;
- pytest;
- flake8.

Консольная версия использует только стандартную библиотеку, веб-версии нужен Django. Установка зависимостей (в виртуальное окружение):
```text
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Запуск программы
Веб-версия (Django). База проекта `data/interest_tracker.sqlite` уже лежит в репозитории; если её нужно создать заново — команды в разделе «База данных SQLite (ПР7)».
```text
python manage.py migrate
python manage.py runserver --insecure
```
Команда `migrate` выполняется один раз: она применяет встроенные миграции Django и создаёт файл `db.sqlite3`. Флаг `--insecure` нужен, потому что в настройках `DEBUG = False`, а при таком значении сервер разработки не раздаёт статические файлы (CSS, JavaScript, логотип); без флага страницы откроются без оформления проекта. После запуска сервера открыть в браузере адрес:
```text
http://127.0.0.1:8000/
```

Системная проверка проекта Django:
```text
python manage.py check
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
- `/interests/` — «Всего интересов: 6», кнопки-фильтры категорий, карточки интересов из базы SQLite, у каждой кнопка «Подробнее»;
- `/interests/?category=2` — только интересы категории «Спорт» (Бег, Стрельба из лука), «Всего интересов: 2»;
- `/interests/available/` — форма выбора пользователя; для Ивана Петрова (`?user=1`) — «Английский язык», «Бег», «Гитара», для Анны Смирновой (`?user=2`) — «Бег», «Изучение веб-разработки на Python», «Стрельба из лука»; для несуществующего пользователя (`?user=999`) — «Пользователь не найден»;
- `/subscriptions/statistics/` — «Отмечено занятий: 12, всего часов: 22,0», таблицы подписок и часов по интересам, интересов по категориям, список «Спорт: 2»;
- `/interests/1/` — Иван Петров: «подписка невозможна» (уже подписан), Анна Смирнова: «можно подписаться»;
- `/interests/2/` — «Бег»: оба пользователя могут подписаться, прежние подписки отменены;
- `/interests/5/` — интерес в архиве: подписка невозможна для всех;
- `/subscriptions/` — «Активных подписок: 4», четыре активные подписки (№1, 3, 4, 6) со значком статуса; отменённые (№2, 5) в список не входят;
- `/subscriptions/1/` — активная подписка, отмечено 13,0 ч;
- `/subscriptions/2/` — отменённая подписка, статус «отменена»;
- `/interests/999/` и `/subscriptions/999/` — страница с сообщением «не найден» и код статуса 404 (формирует view);
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

Веб-страницы на этом этапе проверяются вручную в браузере (адреса из раздела выше); автоматические тесты веб-слоя планируются в следующих работах. После перехода на шаблоны (ПР6) и на базу данных (ПР7) все 17 тестов проходят без изменений: пакет `models/`, `storage.py` и `main.py` не менялись. Слой базы данных ПР7 проверяется командами из раздела «База данных SQLite (ПР7)»: количество записей после импорта, запросы в консоли SQLite, страницы в браузере.

## Проверка качества кода
```text
flake8
```
Если замечаний нет, flake8 ничего не выводит. Каталог `.venv` исключён из проверки. Для сгенерированных Django файлов `manage.py` и `interest_tracker/settings.py` в `.flake8` отключена только проверка длины строки (E501): в них есть длинные строки с путями к классам Django.

## Git
Исходный код хранится в Git-репозитории: https://github.com/Mikle-kekich/Personal-Interes

Проверка состояния репозитория:
```text
git status
```
Коммиты ПР5 начинаются с метки `PR5:`, коммиты ПР6 — с метки `PR6:`, коммиты ПР7 — с метки `PR7:` (например, `PR7: add SQLite database and SQL queries`).

## Текущее состояние и план развития
### Текущий этап разработки (ПР7)
На ПР7 данные проекта перенесены из JSON в базу данных SQLite:
- создана база данных `data/interest_tracker.sqlite`, таблицы созданы командами из `sql/schema.sql` (пять таблиц, первичные и внешние ключи);
- данные перенесены из JSON скриптом `db/import_json.py`, подключение к базе — `db/database.py` (`PRAGMA foreign_keys = ON`);
- 15 SQL-запросов сохранены в `sql/queries.sql`: списки, `WHERE`, `JOIN`, `COUNT` и `SUM`, `GROUP BY`, `HAVING`, подзапрос `NOT IN`;
- Django-представления получают данные из SQLite через `sqlite3` (`row_factory = sqlite3.Row`, параметризованные запросы с `?`) и передают их в шаблоны через контекст;
- страницы списка интересов (с фильтром по категории), активных подписок, поиска доступных интересов и статистики работают с базой данных, в навигацию добавлен раздел «Статистика»;
- консольная версия, JSON-хранилище, страницы интереса и подписки (ПР5–ПР6) и все 17 тестов сохранены.

На следующих практических работах база данных будет подключена к Django с использованием Django ORM.

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

Пока не реализовано: Django ORM не используется (с базой данных проекта работают прямые SQL-запросы через `sqlite3`), страницы интереса и подписки читают JSON, веб-формы отсутствуют.

Планируется:
- перенос сущностей `Category`, `Interest`, `User` и `Subscription` в Django ORM: модели в `models.py` приложений, миграции, подключение базы данных к Django (SQLite / PostgreSQL);
- формы и POST-запросы: оформление и отмена подписки, отметка занятий, добавление интересов и категорий, использование отложенной логики ПР3;
- аутентификация, регистрация и разграничение прав доступа пользователей;
- REST API для интеграции с мобильными или внешними клиентами;
- автоматические тесты веб-слоя и расширение покрытия бизнес-логики;
- контейнеризация приложения с использованием Docker и Docker Compose;
- настройка базового CI/CD пайплайна для автоматической проверки и развёртывания.
