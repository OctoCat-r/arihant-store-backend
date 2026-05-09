DEFAULT_PAGE_SIZE = 50


def paginate_qs(queryset, request):
    try:
        page = max(1, int(request.GET.get('page', 1)))
        size = min(200, max(1, int(request.GET.get('page_size', DEFAULT_PAGE_SIZE))))
    except (TypeError, ValueError):
        page, size = 1, DEFAULT_PAGE_SIZE

    total = queryset.count()
    items = list(queryset.skip((page - 1) * size).limit(size))
    return items, total, page, size
