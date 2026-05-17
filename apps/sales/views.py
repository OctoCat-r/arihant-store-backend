import uuid
import datetime
from rest_framework.decorators import api_view
from .filters import apply_sales_filters
from .models import Sale
from apps.products.models import Product
from core.responses import ok, err, paginated
from core.pagination import paginate_qs


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
    payment_method = data.get('paymentMethod', 'UPI')

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
    if payment_method not in ('UPI', 'Cash', 'Card'):
        return err('paymentMethod must be UPI, Cash, or Card.', 400)

    try:
        product = Product.objects.get(id=product_id)
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

    product.stock = product.stock - qty
    product.sold_30d = product.sold_30d + qty
    product.save()

    return ok(sale.to_dict(), 201)
