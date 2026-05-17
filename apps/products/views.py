import uuid
from rest_framework.decorators import api_view
from .models import Category, Brand, Product
from .filters import build_match, build_sort, raw_to_dict
from core.responses import ok, err, paginated


# ── Categories ──────────────────────────────────────────────────────────────

@api_view(['GET'])
def list_categories(request):
    cats = Category.objects.order_by('name')
    return ok([c.to_dict() for c in cats])


@api_view(['POST'])
def create_category(request):
    data = request.data
    if not data.get('name'):
        return err('name is required.')
    cat = Category(
        id=data.get('id') or f"cat-{uuid.uuid4().hex[:8]}",
        name=data['name'].strip(),
        icon=data.get('icon', ''),
        color=data.get('color', '#7C3AED'),
    )
    cat.save()
    return ok(cat.to_dict(), 201)


@api_view(['PATCH', 'DELETE'])
def category_detail(request, cat_id):
    try:
        cat = Category.objects.get(id=cat_id)
    except Category.DoesNotExist:
        return err('Category not found.', 404)

    if request.method == 'DELETE':
        cat.delete()
        return ok({'deleted': cat_id})

    for field in ('name', 'icon', 'color'):
        if field in request.data:
            setattr(cat, field, request.data[field])
    cat.save()
    return ok(cat.to_dict())


# ── Brands ───────────────────────────────────────────────────────────────────

@api_view(['GET'])
def list_brands(request):
    brands = [b.name for b in Brand.objects.order_by('name')]
    return ok(brands)


@api_view(['POST'])
def create_brand(request):
    name = (request.data.get('name') or '').strip()
    if not name:
        return err('name is required.')
    Brand.objects(name=name).update_one(set__name=name, upsert=True)
    return ok({'name': name}, 201)


# ── Products ─────────────────────────────────────────────────────────────────

@api_view(['GET'])
def list_products(request):
    try:
        page = max(1, int(request.GET.get('page', 1)))
        size = min(200, max(1, int(request.GET.get('page_size', 50))))
    except (TypeError, ValueError):
        page, size = 1, 50

    match = build_match(request)
    sort = build_sort(request)

    pipeline = [
        *([{'$match': match}] if match else []),
        {'$sort': sort},
        {'$facet': {
            'data': [{'$skip': (page - 1) * size}, {'$limit': size}],
            'total': [{'$count': 'n'}],
        }},
    ]

    result = next(iter(Product.objects.aggregate(pipeline)), None)
    if not result:
        return paginated([], 0, page, size)

    total = result['total'][0]['n'] if result.get('total') else 0
    return paginated([raw_to_dict(p) for p in result.get('data', [])], total, page, size)


@api_view(['POST'])
def create_product(request):
    data = request.data
    if not data.get('name') or not data.get('category'):
        return err('name and category are required.')
    prod_id = data.get('id') or uuid.uuid4().hex[:8]
    prod = Product(
        id=prod_id,
        name=data['name'].strip(),
        category=data['category'],
        brand=data.get('brand', ''),
        stock=int(data.get('stock', 0)),
        cost=int(data.get('cost', 0)),
        price=int(data.get('price', 0)),
        compatible_with=data.get('compatibleWith', []),
        color=data.get('color'),
        sku=data.get('sku', f'ARI-{prod_id.upper()}'),
        sold_30d=int(data.get('sold30d', 0)),
        rating=float(data.get('rating', 4.0)),
        added_date=data.get('addedDate', ''),
        low_stock_threshold=int(data.get('lowStockThreshold', 5)),
        image=data.get('image'),
    )
    prod.save()

    # upsert brand
    brand_name = data.get('brand', '').strip()
    if brand_name:
        Brand.objects(name=brand_name).update_one(set__name=brand_name, upsert=True)

    return ok(prod.to_dict(), 201)


@api_view(['GET', 'PATCH', 'DELETE'])
def product_detail(request, prod_id):
    try:
        prod = Product.objects.get(id=prod_id)
    except Product.DoesNotExist:
        return err('Product not found.', 404)

    if request.method == 'GET':
        return ok(prod.to_dict())

    if request.method == 'DELETE':
        prod.delete()
        return ok({'deleted': prod_id})

    # PATCH
    if 'delta' in request.data:
        try:
            prod.stock = max(0, prod.stock + int(request.data['delta']))
        except (TypeError, ValueError):
            return err('delta must be an integer.')

    field_map = {
        'name': 'name', 'category': 'category', 'brand': 'brand',
        'stock': ('stock', int), 'cost': ('cost', int), 'price': ('price', int),
        'compatibleWith': ('compatible_with', list), 'color': 'color',
        'sku': 'sku', 'sold30d': ('sold_30d', int), 'rating': ('rating', float),
        'addedDate': 'added_date', 'lowStockThreshold': ('low_stock_threshold', int),
        'image': 'image',
    }
    for frontend_key, mapping in field_map.items():
        if frontend_key not in request.data:
            continue
        val = request.data[frontend_key]
        if isinstance(mapping, tuple):
            attr, cast = mapping
            setattr(prod, attr, cast(val) if val is not None else val)
        else:
            setattr(prod, mapping, val)
    prod.save()

    if 'brand' in request.data:
        brand_name = request.data['brand'].strip()
        if brand_name:
            Brand.objects(name=brand_name).update_one(set__name=brand_name, upsert=True)

    return ok(prod.to_dict())
