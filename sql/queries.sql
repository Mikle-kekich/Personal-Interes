-- ==========================================
-- Interest Tracker: SQL-запросы проекта
-- ==========================================
-- Проверка запросов (из корня проекта):
--     python -m sqlite3 data/interest_tracker.sqlite
-- Значения (категория 2, пользователь 1) записаны для проверки;
-- в веб-приложении они передаются параметрами "?".
-- Запросы 3 и 4 учебные (простые SELECT и WHERE), остальные
-- используются страницами сайта.


-- ==========================================
-- Списки объектов (SELECT)
-- ==========================================

-- 1. Список категорий (фильтр на странице интересов)
SELECT
    id,
    name
FROM categories
ORDER BY name;

-- 2. Список пользователей (выбор пользователя на странице поиска)
SELECT
    id,
    name,
    email
FROM users
ORDER BY name;

-- 3. Список интересов
SELECT
    id,
    name,
    weekly_goal,
    is_active
FROM interests
ORDER BY name;


-- ==========================================
-- Фильтрация (WHERE)
-- ==========================================

-- 4. Активные интересы с недельной целью не менее 4 часов
SELECT
    id,
    name,
    weekly_goal
FROM interests
WHERE is_active = 1
    AND weekly_goal >= 4
ORDER BY weekly_goal DESC, name;

-- 5. Пользователь по номеру (страница поиска доступных интересов)
SELECT
    id,
    name,
    email
FROM users
WHERE id = 1;


-- ==========================================
-- Соединение таблиц (JOIN)
-- ==========================================

-- 6. Интересы с названиями категорий (страница «Интересы»)
SELECT
    interests.id,
    interests.name,
    categories.name AS category_name,
    interests.weekly_goal,
    interests.is_active
FROM interests
JOIN categories
    ON interests.category_id = categories.id
ORDER BY interests.name;

-- 7. Интересы выбранной категории (фильтр на странице «Интересы»)
SELECT
    interests.id,
    interests.name,
    categories.name AS category_name,
    interests.weekly_goal,
    interests.is_active
FROM interests
JOIN categories
    ON interests.category_id = categories.id
WHERE interests.category_id = 2
ORDER BY interests.name;

-- 8. Активные подписки с именем пользователя и названием интереса
--    (страница «Подписки»)
SELECT
    subscriptions.id,
    users.name AS user_name,
    interests.name AS interest_name,
    subscriptions.start_date,
    subscriptions.is_cancelled
FROM subscriptions
JOIN users
    ON subscriptions.user_id = users.id
JOIN interests
    ON subscriptions.interest_id = interests.id
WHERE subscriptions.is_cancelled = 0
ORDER BY subscriptions.start_date, subscriptions.id;

-- 9. Интересы, на которые пользователь 1 может подписаться:
--    интерес активен и нет его активной подписки (подзапрос NOT IN)
--    (страница «Доступные интересы»)
SELECT
    interests.id,
    interests.name,
    categories.name AS category_name,
    interests.weekly_goal,
    interests.is_active
FROM interests
JOIN categories
    ON interests.category_id = categories.id
WHERE interests.is_active = 1
    AND interests.id NOT IN (
        SELECT subscriptions.interest_id
        FROM subscriptions
        WHERE subscriptions.user_id = 1
            AND subscriptions.is_cancelled = 0
    )
ORDER BY interests.name;


-- ==========================================
-- Агрегатные функции (COUNT, SUM)
-- ==========================================

-- 10. Количество активных подписок (страница «Подписки»)
SELECT
    COUNT(*) AS subscriptions_count
FROM subscriptions
WHERE is_cancelled = 0;

-- 11. Количество занятий и общее число часов (страница «Статистика»)
--     COALESCE заменяет NULL на 0, если занятий нет
SELECT
    COUNT(*) AS activities_count,
    COALESCE(SUM(hours), 0) AS total_hours
FROM activities;


-- ==========================================
-- Группировка (GROUP BY) и фильтрация групп (HAVING)
-- ==========================================

-- 12. Количество активных подписок по интересам (страница «Статистика»)
--     LEFT JOIN сохраняет интересы без активных подписок
SELECT
    interests.name AS interest_name,
    COUNT(subscriptions.id) AS subscriptions_count
FROM interests
LEFT JOIN subscriptions
    ON interests.id = subscriptions.interest_id
    AND subscriptions.is_cancelled = 0
GROUP BY interests.id, interests.name
ORDER BY subscriptions_count DESC, interests.name;

-- 13. Часы занятий по интересам (страница «Статистика»)
--     учитываются все подписки, как в консольной статистике ПР3
SELECT
    interests.name AS interest_name,
    COALESCE(SUM(activities.hours), 0) AS total_hours
FROM interests
LEFT JOIN subscriptions
    ON interests.id = subscriptions.interest_id
LEFT JOIN activities
    ON subscriptions.id = activities.subscription_id
GROUP BY interests.id, interests.name
ORDER BY total_hours DESC, interests.name;

-- 14. Количество интересов по категориям (страница «Статистика»)
SELECT
    categories.name AS category_name,
    COUNT(interests.id) AS interests_count
FROM categories
LEFT JOIN interests
    ON categories.id = interests.category_id
GROUP BY categories.id, categories.name
ORDER BY interests_count DESC, categories.name;

-- 15. Категории, в которых больше одного интереса: HAVING отбирает
--     группы после группировки (страница «Статистика»)
SELECT
    categories.name AS category_name,
    COUNT(interests.id) AS interests_count
FROM categories
JOIN interests
    ON categories.id = interests.category_id
GROUP BY categories.id, categories.name
HAVING COUNT(interests.id) > 1
ORDER BY interests_count DESC, categories.name;
