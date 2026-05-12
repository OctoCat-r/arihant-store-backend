import certifi
import datetime
from pymongo import MongoClient, DESCENDING
from django.conf import settings
from rest_framework.decorators import api_view
from apps.products.models import Product
from core.responses import ok


def _get_db():
    uri = getattr(settings, 'MONGO_URI', None)
    db_name = getattr(settings, 'MONGO_DB', 'arihant_db')
    if uri:
        client = MongoClient(uri, tlsCAFile=certifi.where())
    else:
        client = MongoClient(
            host=getattr(settings, 'MONGO_HOST', 'localhost'),
            port=getattr(settings, 'MONGO_PORT', 27017),
        )
    return client[db_name]


@api_view(['GET'])
def dashboard(request):
    try:
        days = int(request.GET.get('range', 30))
    except (TypeError, ValueError):
        days = 30

    cutoff = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
    db = _get_db()

    # Revenue + profit aggregation
    agg = list(db.sales.aggregate([
        {'$match': {'date': {'$gte': cutoff}}},
        {'$group': {
            '_id': None,
            'total_revenue': {'$sum': '$revenue'},
            'total_profit': {'$sum': '$profit'},
            'total_orders': {'$sum': 1},
        }},
    ]))
    if agg:
        a = agg[0]
        total_rev = a['total_revenue']
        total_profit = a['total_profit']
        total_orders = a['total_orders']
    else:
        total_rev = total_profit = total_orders = 0

    # Stock summary
    total_products = Product.objects.count()
    low_stock = Product.objects.filter(
        __raw__={'$and': [{'stock': {'$gt': 0}}, {'$expr': {'$lte': ['$stock', '$low_stock_threshold']}}]}
    ).count()
    out_of_stock = Product.objects.filter(stock=0).count()

    # Inventory value (stock × cost across all products)
    inv_agg = list(db.products.aggregate([
        {'$group': {'_id': None, 'total': {'$sum': {'$multiply': ['$stock', '$cost']}}}}
    ]))
    inventory_value = inv_agg[0]['total'] if inv_agg else 0

    # Revenue sparkline — last 7 days
    spark_cutoff = (datetime.date.today() - datetime.timedelta(days=6)).isoformat()
    spark_raw = {
        r['_id']: r['rev']
        for r in db.sales.aggregate([
            {'$match': {'date': {'$gte': spark_cutoff}}},
            {'$group': {'_id': '$date', 'rev': {'$sum': '$revenue'}}},
            {'$sort': {'_id': 1}},
        ])
    }
    revenue_spark = [
        {'date': (datetime.date.today() - datetime.timedelta(days=6 - i)).isoformat(),
         'revenue': spark_raw.get(
             (datetime.date.today() - datetime.timedelta(days=6 - i)).isoformat(), 0
         )}
        for i in range(7)
    ]

    # Daily trend — last 14 days (revenue + profit)
    trend_cutoff = (datetime.date.today() - datetime.timedelta(days=13)).isoformat()
    trend_raw = {
        r['_id']: r
        for r in db.sales.aggregate([
            {'$match': {'date': {'$gte': trend_cutoff}}},
            {'$group': {
                '_id': '$date',
                'revenue': {'$sum': '$revenue'},
                'profit': {'$sum': '$profit'},
            }},
            {'$sort': {'_id': 1}},
        ])
    }
    days_list = []
    for i in range(14):
        d = (datetime.date.today() - datetime.timedelta(days=13 - i)).isoformat()
        row = trend_raw.get(d, {})
        days_list.append({
            'date': d,
            'revenue': row.get('revenue', 0),
            'profit': row.get('profit', 0),
        })

    # Revenue by category
    by_category = [
        {'category': r['_id'], 'revenue': r['revenue'], 'profit': r['profit']}
        for r in db.sales.aggregate([
            {'$match': {'date': {'$gte': cutoff}}},
            {'$group': {
                '_id': '$category',
                'revenue': {'$sum': '$revenue'},
                'profit': {'$sum': '$profit'},
            }},
            {'$sort': {'revenue': -1}},
        ])
    ]

    # Top sellers — top 6 products by sold_30d
    top_sellers = [
        {
            'productId': str(p['_id']),
            'name': p.get('name', ''),
            'category': p.get('category', ''),
            'sold30d': p.get('sold_30d', 0),
        }
        for p in db.products.find(
            {'sold_30d': {'$gt': 0}},
            {'name': 1, 'category': 1, 'sold_30d': 1}
        ).sort('sold_30d', DESCENDING).limit(6)
    ]

    return ok({
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
    })


@api_view(['GET'])
def profit_loss(request):
    try:
        days = int(request.GET.get('range', 30))
    except (TypeError, ValueError):
        days = 30

    cutoff = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
    db = _get_db()

    # Totals
    totals = list(db.sales.aggregate([
        {'$match': {'date': {'$gte': cutoff}}},
        {'$group': {
            '_id': None,
            'revenue': {'$sum': '$revenue'},
            'cost': {'$sum': '$cost'},
            'profit': {'$sum': '$profit'},
        }},
    ]))
    if totals:
        t = totals[0]
        total_rev = t['revenue']
        total_cost = t['cost']
        total_profit = t['profit']
    else:
        total_rev = total_cost = total_profit = 0

    opex = round(total_rev * 0.08)
    net_profit = total_profit - opex
    margin = round((total_profit / total_rev * 100), 2) if total_rev else 0

    # Daily trend
    daily_raw = {
        r['_id']: r
        for r in db.sales.aggregate([
            {'$match': {'date': {'$gte': cutoff}}},
            {'$group': {
                '_id': '$date',
                'revenue': {'$sum': '$revenue'},
                'cost': {'$sum': '$cost'},
                'profit': {'$sum': '$profit'},
            }},
            {'$sort': {'_id': 1}},
        ])
    }
    days_list = []
    for i in range(days):
        d = (datetime.date.today() - datetime.timedelta(days=days - 1 - i)).isoformat()
        row = daily_raw.get(d, {})
        days_list.append({
            'date': d,
            'revenue': row.get('revenue', 0),
            'cost': row.get('cost', 0),
            'profit': row.get('profit', 0),
        })

    # By category
    by_cat = [
        {'category': r['_id'], 'revenue': r['revenue'], 'profit': r['profit']}
        for r in db.sales.aggregate([
            {'$match': {'date': {'$gte': cutoff}}},
            {'$group': {
                '_id': '$category',
                'revenue': {'$sum': '$revenue'},
                'profit': {'$sum': '$profit'},
            }},
            {'$sort': {'revenue': -1}},
        ])
    ]

    return ok({
        'totalRevenue': total_rev,
        'totalCost': total_cost,
        'totalProfit': total_profit,
        'opex': opex,
        'netProfit': net_profit,
        'margin': margin,
        'days': days_list,
        'byCategory': by_cat,
    })
