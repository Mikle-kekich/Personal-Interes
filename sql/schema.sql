-- ==========================================
-- Interest Tracker: структура базы данных
-- ==========================================

-- Категория (сфера) интересов
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

-- Пользователь системы
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL
);

-- Интерес: относится к одной категории;
-- is_active: 1 - активен, 0 - в архиве
CREATE TABLE IF NOT EXISTS interests (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category_id INTEGER NOT NULL,
    weekly_goal REAL NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- Подписка пользователя на интерес;
-- is_cancelled: 0 - подписка активна, 1 - отменена
CREATE TABLE IF NOT EXISTS subscriptions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    interest_id INTEGER NOT NULL,
    start_date TEXT NOT NULL,
    is_cancelled INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (interest_id) REFERENCES interests(id)
);

-- Занятие по подписке: дата и затраченные часы
-- (в JSON это словарь hours_by_date внутри подписки)
CREATE TABLE IF NOT EXISTS activities (
    id INTEGER PRIMARY KEY,
    subscription_id INTEGER NOT NULL,
    activity_date TEXT NOT NULL,
    hours REAL NOT NULL,
    FOREIGN KEY (subscription_id) REFERENCES subscriptions(id)
);
