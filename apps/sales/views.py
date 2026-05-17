import uuid
import datetime
from rest_framework.decorators import api_view
from .filters import apply_sales_filters
from .models import Sale
from apps.products.models import Product
from core.responses import ok, err, paginated
from core.pagination import paginate_qs
from core import cache


@api_view(['GET'])
def list_sales(request):
    qs = apply_sales_filters(request)
    items, total, page, size = paginate_qs(qs, request)
    return paginated([s.to_dict() for s in items], total, page, size)


@api_view(['POST'])
def create_sale(request):
    data = request.data
    product_id = (data.get('productId') or '').strip()
    customer = (data.get('customer') or 'Walk-in').strip() or 'Walk-in'
    payment_method = (data.get('paymentMethod') or 'UPI').strip() or 'UPI'

    try:
        qty = int(data.get('qty', 1))
        selling_price = int(data.get('sellingPrice', 0))
    except (TypeError, ValueError):
        return err('qty and sellingPrice must be integers.', 400)

    if not product_id:
        return err('productId is required.', 400)
    if qty < 1:
        return err('qty must be at least 1.', 400)
    if selling_price < 0:
        return err('sellingPrice must be non-negative.', 400)

    try:
        product = Product.objects.only(
            'id', 'name', 'category', 'cost', 'stock', 'sold_30d'
        ).get(id=product_id)
    except Product.DoesNotExist:
        return err('Product not found.', 404)

    if product.stock < qty:
        return err(f'Insufficient stock. Available: {product.stock}', 400)

    revenue = selling_price * qty
    cost = product.cost * qty
    profit = revenue - cost

    sale = Sale(
        id=uuid.uuid4().hex[:8],
        date=datetime.date.today().isoformat(),
        product_id=product.id,
        product_name=product.name,
        category=product.category,
        qty=qty,
        revenue=revenue,
        cost=cost,
        profit=profit,
        customer=customer,
        payment_method=payment_method,
    )
    sale.save()

    # Atomic stock update — avoids race condition from read-modify-write
    Product.objects(id=product_id).update_one(
        dec__stock=qty,
        inc__sold_30d=qty,
    )

    # Invalidate analytics cache — dashboard/P&L data is now stale
    cache.delete_prefix('dashboard_')
    cache.delete_prefix('pl_')

    return ok(sale.to_dict(), 201)
