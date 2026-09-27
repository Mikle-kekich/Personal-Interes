"""Класс Subscription и функции работы с подписками.

Подписка — главная функция приложения: пользователь подписывается
на интерес и отмечает по подписке занятия (дата и затраченные часы).
Здесь же находятся функции расчёта прогресса и рекомендаций
из начального сценария ПР1.
"""
from datetime import date
from typing import Dict, List, Optional

from utils import format_date, get_next_id

from .interests import Interest
from .users import User


class Subscription:
    """Подписка пользователя на интерес с журналом занятий."""

    def __init__(
        self,
        subscription_id: int,
        user: User,
        interest: Interest,
        start_date: str,
    ) -> None:
        """Создать объект подписки.

        Подписка хранит ссылки на объекты User и Interest.
        Журнал занятий hours_by_date: дата ГГГГ-ММ-ДД -> часы.
        """
        self.id = subscription_id
        self.user = user
        self.interest = interest
        self.start_date = start_date
        self.is_cancelled = False
        self.hours_by_date: Dict[str, float] = {}

    @property
    def status(self) -> str:
        """Состояние подписки текстом: «активна» или «отменена»."""
        return "отменена" if self.is_cancelled else "активна"

    def cancel(self) -> None:
        """Отменить подписку (отписаться от интереса)."""
        self.is_cancelled = True

    def add_activity(self, activity_date: date, hours: float) -> None:
        """Отметить занятие: прибавить часы к дате activity_date.

        Вызывает ValueError, если подписка отменена
        или время не в диапазоне от 0 до 24 часов.
        """
        if self.is_cancelled:
            raise ValueError("Подписка отменена, отметить занятие нельзя")
        if not 0 < hours <= 24:
            raise ValueError(
                "Время занятия должно быть больше 0 и не больше 24 ч"
            )
        day = activity_date.isoformat()
        self.hours_by_date[day] = self.hours_by_date.get(day, 0) + hours

    def get_weekly_hours(self, week_date: date) -> float:
        """Посчитать часы за неделю, в которую входит week_date.

        Неделя определяется парой (год, номер недели) из isocalendar().
        """
        week = week_date.isocalendar()[:2]
        total = 0.0
        for day, hours in self.hours_by_date.items():
            if date.fromisoformat(day).isocalendar()[:2] == week:
                total += hours
        return total

    def get_total_hours(self) -> float:
        """Посчитать все часы, отмеченные по подписке."""
        return sum(self.hours_by_date.values())

    def __str__(self) -> str:
        """Вернуть строковое представление подписки."""
        return (
            f"{self.id}. {self.user.name} — «{self.interest.name}», "
            f"с {format_date(self.start_date)}, {self.status}"
        )


def can_subscribe(
    subscriptions: List[Subscription], user: User, interest: Interest
) -> bool:
    """Проверить, можно ли подписать пользователя на интерес.

    Нельзя подписаться на интерес в архиве и нельзя иметь две
    активные подписки одного пользователя на один интерес.
    Отменённая подписка повторной подписке не мешает.
    """
    if not interest.is_active:
        return False
    for subscription in subscriptions:
        if (
            subscription.user.id == user.id
            and subscription.interest.id == interest.id
            and not subscription.is_cancelled
        ):
            return False
    return True


def create_subscription(
    subscriptions: List[Subscription], user: User, interest: Interest
) -> Optional[Subscription]:
    """Оформить подписку с сегодняшней даты и добавить её в список.

    Если подписаться нельзя (см. can_subscribe), вернуть None.
    """
    if not can_subscribe(subscriptions, user, interest):
        return None
    subscription = Subscription(
        get_next_id([item.id for item in subscriptions]),
        user,
        interest,
        date.today().isoformat(),
    )
    subscriptions.append(subscription)
    return subscription


def cancel_subscription(
    subscriptions: List[Subscription], subscription_id: int
) -> bool:
    """Отменить подписку по номеру.

    Подписка не удаляется из списка, меняется только её состояние.
    Вернуть False, если активной подписки с таким номером нет.
    """
    subscription = find_subscription_by_id(subscriptions, subscription_id)
    if subscription is None or subscription.is_cancelled:
        return False
    subscription.cancel()
    return True


def get_subscription_status(
    subscriptions: List[Subscription], user: User, interest: Interest
) -> str:
    """Сформировать сообщение о том, можно ли оформить подписку."""
    if not interest.is_active:
        return f"Интерес «{interest.name}» в архиве, подписка невозможна."
    if can_subscribe(subscriptions, user, interest):
        return f"{user.name} может подписаться на «{interest.name}»."
    return f"{user.name} уже подписан(а) на «{interest.name}»."


def find_subscription_by_id(
    subscriptions: List[Subscription], subscription_id: int
) -> Optional[Subscription]:
    """Найти подписку по номеру; если её нет, вернуть None."""
    for subscription in subscriptions:
        if subscription.id == subscription_id:
            return subscription
    return None


def show_subscriptions(subscriptions: List[Subscription]) -> None:
    """Вывести список подписок."""
    if not subscriptions:
        print("Подписок пока нет.")
        return
    for subscription in subscriptions:
        print(subscription)


def calculate_progress(spent_hours: float, weekly_goal: float) -> float:
    """Рассчитать процент выполнения недельной цели (до десятых долей).

    Вызывает ValueError, если недельная цель не больше нуля.
    """
    if weekly_goal <= 0:
        raise ValueError("Недельная цель должна быть больше нуля")
    return round((spent_hours / weekly_goal) * 100, 1)


def generate_recommendation(
    is_active: bool,
    completion_rate: float,
    spent_hours: float,
    weekly_goal: float,
) -> str:
    """Проанализировать вовлечённость и сформировать рекомендацию."""
    if not is_active:
        return "Подписка отменена. Учёт времени приостановлен."
    elif completion_rate >= 100.0:
        return "Отличный результат! Недельная цель полностью выполнена."
    elif completion_rate >= 50.0:
        remaining_hours = weekly_goal - spent_hours
        return (
            "Хороший темп. "
            f"До выполнения цели осталось {remaining_hours:.1f} ч."
        )
    else:
        remaining_hours = weekly_goal - spent_hours
        return (
            "Внимание: низкая активность. "
            f"Требуется уделить ещё {remaining_hours:.1f} ч."
        )


def display_interest_card(
    subscription: Subscription,
    spent_hours: float,
    completion_rate: float,
    recommendation: str,
) -> None:
    """Вывести карточку интереса по подписке: прогресс и рекомендацию."""
    interest = subscription.interest
    print("=" * 55)
    print(f"КАРТОЧКА ИНТЕРЕСА: {interest.name.upper()}")
    print("=" * 55)
    print(f"Пользователь:       {subscription.user.name}")
    print(f"Категория:          {interest.category.name}")
    print(f"Дата подписки:      {format_date(subscription.start_date)}")
    print(f"Статус подписки:    {subscription.status}")
    print(f"План на неделю:     {interest.weekly_goal:.1f} ч.")
    print(f"Затрачено:          {spent_hours:.1f} ч.")
    print(f"Прогресс:           {completion_rate}%")
    print("-" * 55)
    print(f"Рекомендация:       {recommendation}")
    print("=" * 55)


def get_statistics(
    interests: List[Interest], subscriptions: List[Subscription]
) -> Dict[str, float]:
    """Посчитать все отмеченные часы по каждому интересу.

    Возвращает словарь {название интереса: часы}.
    """
    statistics = {}
    for interest in interests:
        statistics[interest.name] = sum(
            subscription.get_total_hours()
            for subscription in subscriptions
            if subscription.interest.id == interest.id
        )
    return statistics


def show_statistics(statistics: Dict[str, float]) -> None:
    """Вывести часы по каждому интересу и общий итог."""
    for name, hours in statistics.items():
        print(f"{name:<34} {hours:>6.1f} ч.")
    total = sum(statistics.values())
    print(f"Всего затрачено: {total:.1f} ч.")
    if total > 0:
        best_name = max(statistics, key=lambda name: statistics[name])
        print(f"Больше всего времени: {best_name}")
