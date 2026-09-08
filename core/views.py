from django.shortcuts import render
from django.conf import settings

def home_view(request):
    """
    Renders the central system overview page.
    """
    context = {
        'db_name': settings.DATABASES['default']['NAME'],
        'current_year': 2026,
    }
    return render(request, 'home.html', context)
