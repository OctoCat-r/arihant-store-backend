import datetime
from .models import Sale

TODAY = '2026-04-26'  # seed reference date; swap to datetime.date.today().isoformat() in prod


def apply_sales_filters(request):
    qs = Sale.objects

    try:
        days = int(request.GET.get('range', 30))
    except (TypeError, ValueError):
        days = 30

    cutoff = (datetime.date.fromisoformat(TODAY) - datetime.timedelta(days=days)).isoformat()
    qs = qs.filter(date__gte=cutoff)

    category = request.GET.get('category', '').strip()
    if category and category != 'all':
        qs = qs.filter(category=category)

    pm = request.GET.get('payment_method', '').strip()
    if pm and pm != 'all':
        qs = qs.filter(payment_method=pm)

    return qs.order_by('-date')
