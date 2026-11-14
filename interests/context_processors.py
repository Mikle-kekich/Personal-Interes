from interests.models import Interest


def interest_context(request):
    """Общие данные навигации, один COUNT при рендеринге страницы."""
    return {
        "app_title": "Personal-Interes",
        "catalog_interests_count": Interest.objects.count(),
    }
