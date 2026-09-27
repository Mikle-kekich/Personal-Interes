"""Точка запуска приложения «Система управления личными интересами»."""
from pathlib import Path
from typing import List

from models import Category, Interest, Subscription, User
from models.categories import (
    add_category,
    find_category_by_id,
    show_categories,
)
from models.interests import (
    add_interest,
    filter_interests_by_category,
    find_interest_by_id,
    find_interests,
    show_interests,
    sort_interests,
)
from models.subscriptions import (
    calculate_progress,
    cancel_subscription,
    create_subscription,
    display_interest_card,
    find_subscription_by_id,
    generate_recommendation,
    get_statistics,
    get_subscription_status,
    show_statistics,
    show_subscriptions,
)
from models.users import add_user, find_user, find_user_by_id, show_users
from storage import (
    load_categories,
    load_interests,
    load_subscriptions,
    load_users,
    save_categories,
    save_interests,
    save_subscriptions,
    save_users,
)
from utils import input_date, input_float, input_int

DATA_DIR = Path(__file__).parent / "data"
CATEGORIES_FILE = DATA_DIR / "categories.json"
INTERESTS_FILE = DATA_DIR / "interests.json"
USERS_FILE = DATA_DIR / "users.json"
SUBSCRIPTIONS_FILE = DATA_DIR / "subscriptions.json"


def print_menu() -> None:
    """Вывести меню приложения."""
    print("\n=== Система управления личными интересами ===")
    print("Подписки:")
    print(" 1. Подписаться на интерес")
    print(" 2. Отменить подписку")
    print(" 3. Показать подписки")
    print(" 4. Отметить занятие по подписке")
    print(" 5. Прогресс по подписке за неделю")
    print(" 6. Статистика по интересам")
    print("Интересы и категории:")
    print(" 7. Показать интересы")
    print(" 8. Найти интерес по названию")
    print(" 9. Отсортировать интересы по недельной цели")
    print("10. Показать интересы категории")
    print("11. Добавить интерес")
    print("12. Добавить категорию")
    print("Пользователи:")
    print("13. Показать пользователей")
    print("14. Найти пользователя")
    print("15. Добавить пользователя")
    print(" 0. Выход")


def create_new_subscription(
    subscriptions: List[Subscription],
    users: List[User],
    interests: List[Interest],
) -> None:
    """Подписка: выбрать пользователя и интерес, оформить подписку."""
    show_users(users)
    user = find_user_by_id(users, input_int("Номер пользователя: "))
    if user is None:
        print("Пользователь не найден.")
        return
    show_interests(interests)
    interest = find_interest_by_id(interests, input_int("Номер интереса: "))
    if interest is None:
        print("Интерес не найден.")
        return
    subscription = create_subscription(subscriptions, user, interest)
    if subscription is None:
        print(get_subscription_status(subscriptions, user, interest))
        return
    save_subscriptions(SUBSCRIPTIONS_FILE, subscriptions)
    print(f"Подписка оформлена: {subscription}")


def add_new_activity(subscriptions: List[Subscription]) -> None:
    """Отметка занятия: выбрать подписку, ввести дату и часы."""
    show_subscriptions(subscriptions)
    subscription_id = input_int("Номер подписки: ")
    subscription = find_subscription_by_id(subscriptions, subscription_id)
    if subscription is None:
        print("Подписка не найдена.")
        return
    activity_date = input_date("Дата занятия (ДД.ММ.ГГГГ): ")
    hours = input_float("Затрачено часов: ")
    subscription.add_activity(activity_date, hours)
    save_subscriptions(SUBSCRIPTIONS_FILE, subscriptions)
    print("Занятие отмечено.")


def show_progress(subscriptions: List[Subscription]) -> None:
    """Прогресс: вывести карточку интереса по подписке за неделю."""
    show_subscriptions(subscriptions)
    subscription_id = input_int("Номер подписки: ")
    subscription = find_subscription_by_id(subscriptions, subscription_id)
    if subscription is None:
        print("Подписка не найдена.")
        return
    week_date = input_date("Любая дата нужной недели (ДД.ММ.ГГГГ): ")
    weekly_goal = subscription.interest.weekly_goal
    spent_hours = subscription.get_weekly_hours(week_date)
    completion_rate = calculate_progress(spent_hours, weekly_goal)
    recommendation = generate_recommendation(
        not subscription.is_cancelled,
        completion_rate,
        spent_hours,
        weekly_goal,
    )
    display_interest_card(
        subscription, spent_hours, completion_rate, recommendation
    )


def create_new_interest(
    interests: List[Interest], categories: List[Category]
) -> None:
    """Добавление интереса: ввести название, выбрать категорию и цель."""
    name = input("Название интереса: ")
    show_categories(categories)
    category_id = input_int("Номер категории: ")
    category = find_category_by_id(categories, category_id)
    if category is None:
        print("Категория не найдена.")
        return
    weekly_goal = input_float("План на неделю, ч: ")
    add_interest(interests, name, category, weekly_goal)
    save_interests(INTERESTS_FILE, interests)
    print("Интерес добавлен.")


def run_action(
    choice: str,
    categories: List[Category],
    interests: List[Interest],
    users: List[User],
    subscriptions: List[Subscription],
) -> None:
    """Выполнить пункт меню с номером choice."""
    if choice == "1":
        create_new_subscription(subscriptions, users, interests)
    elif choice == "2":
        show_subscriptions(subscriptions)
        subscription_id = input_int("Номер подписки для отмены: ")
        if cancel_subscription(subscriptions, subscription_id):
            save_subscriptions(SUBSCRIPTIONS_FILE, subscriptions)
            print("Подписка отменена.")
        else:
            print("Активной подписки с таким номером нет.")
    elif choice == "3":
        show_subscriptions(subscriptions)
    elif choice == "4":
        add_new_activity(subscriptions)
    elif choice == "5":
        show_progress(subscriptions)
    elif choice == "6":
        show_statistics(get_statistics(interests, subscriptions))
    elif choice == "7":
        show_interests(interests)
    elif choice == "8":
        query = input("Часть названия: ")
        show_interests(find_interests(interests, query))
    elif choice == "9":
        show_interests(sort_interests(interests))
    elif choice == "10":
        show_categories(categories)
        category_id = input_int("Номер категории: ")
        category = find_category_by_id(categories, category_id)
        if category is None:
            print("Категория не найдена.")
        else:
            show_interests(filter_interests_by_category(interests, category))
    elif choice == "11":
        create_new_interest(interests, categories)
    elif choice == "12":
        add_category(categories, input("Название категории: "))
        save_categories(CATEGORIES_FILE, categories)
        print("Категория добавлена.")
    elif choice == "13":
        show_users(users)
    elif choice == "14":
        query = input("Часть имени или почты: ")
        show_users(find_user(users, query))
    elif choice == "15":
        name = input("Имя пользователя: ")
        email = input("Электронная почта: ")
        add_user(users, name, email)
        save_users(USERS_FILE, users)
        print("Пользователь добавлен.")
    else:
        print("Такого пункта нет в меню.")


def main() -> None:
    """Точка запуска: загрузить объекты из JSON и запустить цикл меню."""
    categories = load_categories(CATEGORIES_FILE)
    interests = load_interests(INTERESTS_FILE, categories)
    users = load_users(USERS_FILE)
    subscriptions = load_subscriptions(SUBSCRIPTIONS_FILE, users, interests)

    while True:
        print_menu()
        choice = input("Выберите действие: ").strip()
        if choice == "0":
            print("Работа завершена.")
            break
        try:
            run_action(choice, categories, interests, users, subscriptions)
        except (ValueError, OSError) as error:
            print(f"Ошибка: {error}")


if __name__ == "__main__":
    main()
