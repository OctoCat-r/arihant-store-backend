from .models import Product


def apply_product_filters(request) -> 'QuerySet':
    qs = Product.objects

    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            __raw__={
                '$or': [
                    {'name': {'$regex': q, '$options': 'i'}},
                    {'brand': {'$regex': q, '$options': 'i'}},
                    {'sku': {'$regex': q, '$options': 'i'}},
                    {'compatible_with': {'$regex': q, '$options': 'i'}},
                ]
            }
        )

    category = request.GET.get('category', '').strip()
    if category and category != 'all':
        qs = qs.filter(category=category)

    brands = request.GET.getlist('brands')
    if brands:
        qs = qs.filter(brand__in=brands)

    colors = request.GET.getlist('colors')
    if colors:
        qs = qs.filter(color__in=colors)

    compat = request.GET.getlist('compat')
    if compat:
        qs = qs.filter(compatible_with__in=compat)

    stock_filter = request.GET.get('stock', 'all')
    if stock_filter == 'inStock':
        qs = qs.filter(__raw__={'$expr': {'$gt': ['$stock', '$low_stock_threshold']}})
    elif stock_filter == 'low':
        qs = qs.filter(__raw__={
            '$and': [
                {'stock': {'$gt': 0}},
                {'$expr': {'$lte': ['$stock', '$low_stock_threshold']}},
            ]
        })
    elif stock_filter == 'out':
        qs = qs.filter(stock=0)

    price_min = request.GET.get('price_min', '')
    if price_min:
        try:
            qs = qs.filter(price__gte=int(price_min))
        except ValueError:
            pass

    price_max = request.GET.get('price_max', '')
    if price_max:
        try:
            qs = qs.filter(price__lte=int(price_max))
        except ValueError:
            pass

    sort_by = request.GET.get('sort_by', 'name')
    sort_map = {
        'name': 'name',
        'priceAsc': 'price',
        'priceDesc': '-price',
        'stock': 'stock',
        'sales': '-sold_30d',
    }
    qs = qs.order_by(sort_map.get(sort_by, 'name'))

    return qs
