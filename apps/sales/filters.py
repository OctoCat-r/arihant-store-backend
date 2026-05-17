import datetime
from .models import Sale


def apply_sales_filters(request):
    qs = Sale.objects

    try:
        days = int(request.GET.get('range', 30))
    except (TypeError, ValueError):
        days = 30

    cutoff = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
    qs = qs.filter(date__gte=cutoff)

    category = request.GET.get('category', '').strip()
    if category and category != 'all':
        qs = qs.filter(category=category)

    return qs.order_by('-date')
