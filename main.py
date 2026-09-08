from datetime import date 

# 1. Данные об интересе 
interest_name: str = 'Изучение веб разработки на python'
category: str = 'Программирование'
created_date: date = date(2026, 9, 8)
is_active: bool = True

# 2. Числовые параметры и демонстрация преобразования типов
weekly_goal_hours: float = 8.0
spent_hours_raw: str = '6.5'
#Для демонмт ошибки закоментил 
#spent_hours: float = float(spent_hours_raw)


# 3. Арифметические операции и расчёт прогресса
completion_rate: float = round((spent_hours / weekly_goal_hours)*100,1)

# 4. Логика принятия решений (ветвления)
if not is_active:
    status_message = 'Интерес находится в архиве. Учёт времени приостановлен.'
elif completion_rate >= 100:
    status_message = 'Отличный результат! Недельная цель полностью выполнена.'
elif completion_rate >= 50 :
    remaining_hours = weekly_goal_hours - spent_hours
    status_message = f'Хороший темп. До выполнения цели осталось {remaining_hours:.1f} ч.'
else:
    remaining_hours = weekly_goal_hours - spent_hours
    status_message = f'Внимание: низкая активность. Требуется уделить ещё {remaining_hours:.1f} ч.'

# 5. Форматированный вывод результатов
print('=' * 50)
print(f"КАРТОЧКА ИНТЕРЕСА: {interest_name.upper()}")
print("=" * 50)
print(f"Категория:          {category}")
print(f"Дата добавления:    {created_date}")
print(f"Статус активности:  {'Активен' if is_active else 'Архивирован'}")
print(f"План на неделю:     {weekly_goal_hours} ч.")
print(f"Затрачено:          {spent_hours} ч.")
print(f"Прогресс:           {completion_rate}%")
print("-" * 50)
print(f"Рекомендация:       {status_message}")
print("=" * 50)


