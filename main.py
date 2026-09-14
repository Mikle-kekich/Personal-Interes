from datetime import date


def calculate_progress(spent_hours_raw: str, weekly_goal: float) -> tuple[float, float]:
    
    #Функция 2: Валидация и расчёт прогресса по целям.

    
    spent_hours: float = float(spent_hours_raw)
    completion_rate: float = round((spent_hours / weekly_goal) * 100, 1)
    return spent_hours, completion_rate


def generate_recommendation(is_active: bool, completion_rate: float, spent_hours: float, weekly_goal: float) -> str:
    
    #Функция 3: Анализ вовлечённости и генерация рекомендаций.

    
    if not is_active:
        return "Интерес находится в архиве. Учёт времени приостановлен."
    elif completion_rate >= 100.0:
        return "Отличный результат! Недельная цель полностью выполнена."
    elif completion_rate >= 50.0:
        remaining_hours: float = weekly_goal - spent_hours
        return f"Хороший темп. До выполнения цели осталось {remaining_hours:.1f} ч."
    else:
        remaining_hours: float = weekly_goal - spent_hours
        return f"Внимание: низкая активность. Требуется уделить ещё {remaining_hours:.1f} ч."


def display_interest_card(
    name: str,
    category: str,
    created_date: date,
    is_active: bool,
    weekly_goal: float,
    spent_hours: float,
    completion_rate: float,
    recommendation: str
) -> None:
    
    #Функция 1: Каталогизация и учёт параметров увлечений.
    
    status_title: str = "Активен" if is_active else "Архивирован"

    print("=" * 55)
    print(f"КАРТОЧКА ИНТЕРЕСА: {name.upper()}")
    print("=" * 55)
    print(f"Категория:          {category}")
    print(f"Дата добавления:    {created_date}")
    print(f"Статус активности:  {status_title}")
    print(f"План на неделю:     {weekly_goal:.1f} ч.")
    print(f"Затрачено:          {spent_hours:.1f} ч.")
    print(f"Прогресс:           {completion_rate}%")
    print("-" * 55)
    print(f"Рекомендация:       {recommendation}")
    print("=" * 55)


# --- Основной сценарий выполнения ---
if __name__ == "__main__":
    # Исходные данные сущности Interest
    interest_title: str = "Изучение веб-разработки на Python"
    interest_category: str = "Программирование"
    date_added: date = date(2026, 9, 8)
    is_currently_active: bool = True
    weekly_target_hours: float = 8.0
    input_hours_str: str = "6.5"

    # Вызов функции 2: валидация и расчёт прогресса
    hours_spent, progress_percent = calculate_progress(
        spent_hours_raw=input_hours_str,
        weekly_goal=weekly_target_hours
    )

    # Вызов функции 3: анализ вовлечённости и получение рекомендации
    advice: str = generate_recommendation(
        is_active=is_currently_active,
        completion_rate=progress_percent,
        spent_hours=hours_spent,
        weekly_goal=weekly_target_hours
    )

    # Вызов функции 1: отображение карточки увлечения
    display_interest_card(
        name=interest_title,
        category=interest_category,
        created_date=date_added,
        is_active=is_currently_active,
        weekly_goal=weekly_target_hours,
        spent_hours=hours_spent,
        completion_rate=progress_percent,
        recommendation=advice
    )