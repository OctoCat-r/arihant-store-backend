import datetime
from mongoengine.connection import get_db
from rest_framework.decorators import api_view
from core.responses import ok
from core import cache

_DASHBOARD_TTL = 30  # seconds
_PL_TTL = 30


def _parse_range(request) -> int:
    try:
        return max(1, int(request.GET.get('range', 30)))
    except (TypeError, ValueError):
        return 30


def _cutoff(days: int) -> str:
    return (datetime.date.today() - datetime.timedelta(days=days)).isoformat()


def _fill_dates(raw: dict, days: int, keys: list) -> list:
    today = datetime.date.today()
    result = []
    for i in range(days):
        d = (today - datetime.timedelta(days=days - 1 - i)).isoformat()
        row = raw.get(d, {})
        result.append({'date': d, **{k: row.get(k, 0) for k in keys}})
    return result


@api_view(['GET'])
def dashboard(request):
    days = _parse_range(request)
    cache_key = f'dashboard_{days}'

    hit = cache.get(cache_key, _DASHBOARD_TTL)
    if hit is not None:
        return ok(hit)

    db = get_db()
    main_cutoff = _cutoff(days)
    spark_cutoff = _cutoff(6)
    trend_cutoff = _cutoff(13)
    broad_cutoff = min(main_cutoff, spark_cutoff, trend_cutoff)

    # One round trip for all sales data
    sales_result = next(iter(db.sales.aggregate([
        {'$match': {'date': {'$gte': broad_cutoff}}},
        {'$facet': {
            'totals': [
                {'$match': {'date': {'$gte': main_cutoff}}},
                {'$group': {'_id': None, 'revenue': {'$sum': '$revenue'},
                            'profit': {'$sum': '$profit'}, 'orders': {'$sum': 1}}},
            ],
            'spark': [
                {'$match': {'date': {'$gte': spark_cutoff}}},
                {'$group': {'_id': '$date', 'rev': {'$sum': '$revenue'}}},
                {'$sort': {'_id': 1}},
            ],
            'trend': [
                {'$match': {'date': {'$gte': trend_cutoff}}},
                {'$group': {'_id': '$date', 'revenue': {'$sum': '$revenue'},
                            'profit': {'$sum': '$profit'}}},
                {'$sort': {'_id': 1}},
            ],
            'by_category': [
                {'$match': {'date': {'$gte': main_cutoff}}},
                {'$group': {'_id': '$category', 'revenue': {'$sum': '$revenue'},
                            'profit': {'$sum': '$profit'}}},
                {'$sort': {'revenue': -1}},
            ],
        }},
    ])), {})

    totals_raw = (sales_result.get('totals') or [{}])[0] or {}
    total_rev = totals_raw.get('revenue', 0)
    total_profit = totals_raw.get('profit', 0)
    total_orders = totals_raw.get('orders', 0)

    spark_map = {r['_id']: r['rev'] for r in sales_result.get('spark', [])}
    today = datetime.date.today()
    revenue_spark = [
        {'date': (today - datetime.timedelta(days=6 - i)).isoformat(),
         'revenue': spark_map.get((today - datetime.timedelta(days=6 - i)).isoformat(), 0)}
        for i in range(7)
    ]

    trend_map = {r['_id']: r for r in sales_result.get('trend', [])}
    days_list = _fill_dates(trend_map, 14, ['revenue', 'profit'])

    by_category = [
        {'category': r['_id'], 'revenue': r['revenue'], 'profit': r['profit']}
        for r in sales_result.get('by_category', [])
    ]

    # One round trip for all product data
    products_result = next(iter(db.products.aggregate([
        {'$facet': {
            'counts': [
                {'$group': {'_id': None, 'total': {'$sum': 1},
                            'inventory_value': {'$sum': {'$multiply': ['$stock', '$cost']}}}},
            ],
            'low_stock': [
                {'$match': {'$and': [{'stock': {'$gt': 0}},
                                     {'$expr': {'$lte': ['$stock', '$low_stock_threshold']}}]}},
                {'$count': 'n'},
            ],
            'out_of_stock': [
                {'$match': {'stock': 0}},
                {'$count': 'n'},
            ],
            'top_sellers': [
                {'$match': {'sold_30d': {'$gt': 0}}},
                {'$sort': {'sold_30d': -1}},
                {'$limit': 6},
                {'$project': {'name': 1, 'category': 1, 'sold_30d': 1}},
            ],
        }},
    ])), {})

    counts_raw = (products_result.get('counts') or [{}])[0] or {}
    total_products = counts_raw.get('total', 0)
    inventory_value = counts_raw.get('inventory_value', 0)
    low_stock = (products_result.get('low_stock') or [{}])[0].get('n', 0)
    out_of_stock = (products_result.get('out_of_stock') or [{}])[0].get('n', 0)
    top_sellers = [
        {'productId': str(p['_id']), 'name': p.get('name', ''),
         'category': p.get('category', ''), 'sold30d': p.get('sold_30d', 0)}
        for p in products_result.get('top_sellers', [])
    ]

    data = {
        'revenue': total_rev,
        'profit': total_profit,
        'orders': total_orders,
        'avgOrder': round(total_rev / total_orders) if total_orders else 0,
        'products': total_products,
        'lowStock': low_stock,
        'outOfStock': out_of_stock,
        'inventoryValue': inventory_value,
        'revenueSpark': revenue_spark,
        'days': days_list,
        'byCategory': by_category,
        'topSellers': top_sellers,
    }

    cache.put(cache_key, data)
    return ok(data)


@api_view(['GET'])
def profit_loss(request):
    days = _parse_range(request)
    cache_key = f'pl_{days}'

    hit = cache.get(cache_key, _PL_TTL)
    if hit is not None:
        return ok(hit)

    db = get_db()
    cutoff = _cutoff(days)

    result = next(iter(db.sales.aggregate([
        {'$match': {'date': {'$gte': cutoff}}},
        {'$facet': {
            'totals': [
                {'$group': {'_id': None, 'revenue': {'$sum': '$revenue'},
                            'cost': {'$sum': '$cost'}, 'profit': {'$sum': '$profit'}}},
            ],
            'by_day': [
                {'$group': {'_id': '$date', 'revenue': {'$sum': '$revenue'},
                            'cost': {'$sum': '$cost'}, 'profit': {'$sum': '$profit'}}},
                {'$sort': {'_id': 1}},
            ],
            'by_category': [
                {'$group': {'_id': '$category', 'revenue': {'$sum': '$revenue'},
                            'profit': {'$sum': '$profit'}}},
                {'$sort': {'revenue': -1}},
            ],
        }},
    ])), {})

    totals_raw = (result.get('totals') or [{}])[0] or {}
    total_rev = totals_raw.get('revenue', 0)
    total_cost = totals_raw.get('cost', 0)
    total_profit = totals_raw.get('profit', 0)

    opex = round(total_rev * 0.08)
    net_profit = total_profit - opex
    margin = round((total_profit / total_rev * 100), 2) if total_rev else 0

    day_map = {r['_id']: r for r in result.get('by_day', [])}
    days_list = _fill_dates(day_map, days, ['revenue', 'cost', 'profit'])

    by_cat = [
        {'category': r['_id'], 'revenue': r['revenue'], 'profit': r['profit']}
        for r in result.get('by_category', [])
    ]

    data = {
        'totalRevenue': total_rev,
        'totalCost': total_cost,
        'totalProfit': total_profit,
        'opex': opex,
        'netProfit': net_profit,
        'margin': margin,
        'days': days_list,
        'byCategory': by_cat,
    }

    cache.put(cache_key, data)
    return ok(data)
