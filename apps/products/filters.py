from .models import Product


def build_match(request) -> dict:
    conditions = []

    q = request.GET.get('q', '').strip()
    if q:
        conditions.append({'$or': [
            {'name': {'$regex': q, '$options': 'i'}},
            {'brand': {'$regex': q, '$options': 'i'}},
            {'sku': {'$regex': q, '$options': 'i'}},
            {'compatible_with': {'$regex': q, '$options': 'i'}},
        ]})

    category = request.GET.get('category', '').strip()
    if category and category != 'all':
        conditions.append({'category': category})

    brands = request.GET.getlist('brands')
    if brands:
        conditions.append({'brand': {'$in': brands}})

    colors = request.GET.getlist('colors')
    if colors:
        conditions.append({'color': {'$in': colors}})

    compat = request.GET.getlist('compat')
    if compat:
        conditions.append({'compatible_with': {'$in': compat}})

    stock_filter = request.GET.get('stock', 'all')
    if stock_filter == 'inStock':
        conditions.append({'$expr': {'$gt': ['$stock', '$low_stock_threshold']}})
    elif stock_filter == 'low':
        conditions.append({'stock': {'$gt': 0}})
        conditions.append({'$expr': {'$lte': ['$stock', '$low_stock_threshold']}})
    elif stock_filter == 'out':
        conditions.append({'stock': 0})

    price_min = request.GET.get('price_min', '')
    if price_min:
        try:
            conditions.append({'price': {'$gte': int(price_min)}})
        except ValueError:
            pass

    price_max = request.GET.get('price_max', '')
    if price_max:
        try:
            conditions.append({'price': {'$lte': int(price_max)}})
        except ValueError:
            pass

    if not conditions:
        return {}
    return conditions[0] if len(conditions) == 1 else {'$and': conditions}


def build_sort(request) -> dict:
    sort_map = {
        'name': {'name': 1},
        'priceAsc': {'price': 1},
        'priceDesc': {'price': -1},
        'stock': {'stock': 1},
        'sales': {'sold_30d': -1},
    }
    return sort_map.get(request.GET.get('sort_by', 'name'), {'name': 1})


def raw_to_dict(p: dict) -> dict:
    return {
        'id': str(p.get('_id', '')),
        'name': p.get('name', ''),
        'category': p.get('category', ''),
        'brand': p.get('brand', ''),
        'stock': p.get('stock', 0),
        'cost': p.get('cost', 0),
        'price': p.get('price', 0),
        'compatibleWith': p.get('compatible_with', []),
        'color': p.get('color'),
        'sku': p.get('sku', ''),
        'sold30d': p.get('sold_30d', 0),
        'rating': round(float(p.get('rating', 4.0)), 2),
        'addedDate': p.get('added_date', ''),
        'lowStockThreshold': p.get('low_stock_threshold', 5),
        'image': p.get('image'),
    }
