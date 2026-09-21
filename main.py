"""Точка запуска приложения «Система управления личными интересами»."""
from pathlib import Path

from activities import (
    add_activity,
    calculate_progress,
    cancel_activity,
    generate_recommendation,
    get_statistics,
    get_weekly_hours,
)
from interests import (
    add_interest,
    find_interests,
    get_interest,
    sort_interests,
)
from storage import (
    load_activities,
    load_interests,
    save_activities,
    save_interests,
)
from utils import format_date, input_date, input_float, input_int

DATA_DIR = Path(__file__).parent / "data"
INTERESTS_FILE = DATA_DIR / "interests.json"
ACTIVITIES_FILE = DATA_DIR / "activities.json"


def show_interests(items: list[dict]) -> None:
    """Вывести интересы в виде таблицы."""
    if not items:
        print("Интересы не найдены.")
        return
    print(
        f"{'№':<3} {'Название':<34} {'Категория':<16} "
        f"{'Цель, ч':>7}  Статус"
    )
    for interest in items:
        status = "Активен" if interest["is_active"] else "Архивирован"
        print(
            f"{interest['id']:<3} {interest['name']:<34} "
            f"{interest['category']:<16} {interest['weekly_goal']:>7.1f}  "
            f"{status}"
        )


def show_activities(
    activities: list[dict], interests: dict[int, dict]
) -> None:
    """Вывести записи активности с названием интереса и датой."""
    if not activities:
        print("Записей активности пока нет.")
        return
    print(f"{'№':<3} {'Дата':<10}  {'Интерес':<34} Часы")
    for activity in activities:
        interest = interests.get(activity["interest_id"])
        name = interest["name"] if interest else "—"
        print(
            f"{activity['id']:<3} "
            f"{format_date(activity['activity_date']):<10}  "
            f"{name:<34} {activity['hours']:.1f}"
        )


def display_interest_card(
    interest: dict,
    spent_hours: float,
    completion_rate: float,
    recommendation: str,
) -> None:
    """Вывести карточку интереса с прогрессом и рекомендацией."""
    status_title = "Активен" if interest["is_active"] else "Архивирован"

    print("=" * 55)
    print(f"КАРТОЧКА ИНТЕРЕСА: {interest['name'].upper()}")
    print("=" * 55)
    print(f"Категория:          {interest['category']}")
    print(f"Дата добавления:    {format_date(interest['created_date'])}")
    print(f"Статус активности:  {status_title}")
    print(f"План на неделю:     {interest['weekly_goal']:.1f} ч.")
    print(f"Затрачено:          {spent_hours:.1f} ч.")
    print(f"Прогресс:           {completion_rate}%")
    print("-" * 55)
    print(f"Рекомендация:       {recommendation}")
    print("=" * 55)


def show_statistics(statistics: dict[str, float]) -> None:
    """Вывести часы по каждому интересу и общий итог."""
    for name, hours in statistics.items():
        print(f"{name:<34} {hours:>6.1f} ч.")
    total = sum(statistics.values())
    print(f"Всего затрачено: {total:.1f} ч.")
    if total > 0:
        best_name = max(statistics, key=statistics.get)
        print(f"Больше всего времени: {best_name}")


def print_menu() -> None:
    """Вывести меню приложения."""
    print("\n=== Система управления личными интересами ===")
    print("1. Показать интересы")
    print("2. Найти интерес по названию")
    print("3. Отсортировать интересы по недельной цели")
    print("4. Добавить интерес")
    print("5. Записать активность")
    print("6. Отменить запись активности")
    print("7. Показать записи активности")
    print("8. Прогресс интереса за неделю")
    print("9. Статистика")
    print("0. Выход")


def run_action(
    choice: str, interests: dict[int, dict], activities: list[dict]
) -> None:
    """Выполнить пункт меню с номером choice."""
    if choice == "1":
        show_interests(list(interests.values()))
    elif choice == "2":
        query = input("Часть названия: ")
        show_interests(find_interests(interests, query))
    elif choice == "3":
        show_interests(sort_interests(interests))
    elif choice == "4":
        name = input("Название интереса: ")
        category = input("Категория: ")
        weekly_goal = input_float("План на неделю, ч: ")
        add_interest(interests, name, category, weekly_goal)
        save_interests(INTERESTS_FILE, interests)
        print("Интерес добавлен.")
    elif choice == "5":
        show_interests(list(interests.values()))
        interest_id = input_int("Номер интереса: ")
        activity_date = input_date("Дата занятия (ДД.ММ.ГГГГ): ")
        hours = input_float("Затрачено часов: ")
        add_activity(activities, interests, interest_id, activity_date, hours)
        save_activities(ACTIVITIES_FILE, activities)
        print("Запись активности добавлена.")
    elif choice == "6":
        show_activities(activities, interests)
        activity_id = input_int("Номер записи для отмены: ")
        cancel_activity(activities, activity_id)
        save_activities(ACTIVITIES_FILE, activities)
        print("Запись активности отменена.")
    elif choice == "7":
        show_activities(activities, interests)
    elif choice == "8":
        show_interests(list(interests.values()))
        interest = get_interest(interests, input_int("Номер интереса: "))
        week_date = input_date("Любая дата нужной недели (ДД.ММ.ГГГГ): ")
        weekly_goal = interest["weekly_goal"]
        spent_hours = get_weekly_hours(activities, interest["id"], week_date)
        completion_rate = calculate_progress(spent_hours, weekly_goal)
        recommendation = generate_recommendation(
            interest["is_active"], completion_rate, spent_hours, weekly_goal
        )
        display_interest_card(
            interest, spent_hours, completion_rate, recommendation
        )
    elif choice == "9":
        show_statistics(get_statistics(interests, activities))
    else:
        print("Такого пункта нет в меню.")


def main() -> None:
    """Точка запуска: загрузить данные из JSON и запустить цикл меню."""
    interests = load_interests(INTERESTS_FILE)
    activities = load_activities(ACTIVITIES_FILE)

    while True:
        print_menu()
        choice = input("Выберите действие: ").strip()
        if choice == "0":
            print("Работа завершена.")
            break
        try:
            run_action(choice, interests, activities)
        except (ValueError, OSError) as error:
            print(f"Ошибка: {error}")


if __name__ == "__main__":
    main()
