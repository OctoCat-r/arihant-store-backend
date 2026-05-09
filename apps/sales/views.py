from rest_framework.decorators import api_view
from .filters import apply_sales_filters
from core.responses import ok, paginated
from core.pagination import paginate_qs


@api_view(['GET'])
def list_sales(request):
    qs = apply_sales_filters(request)
    items, total, page, size = paginate_qs(qs, request)
    return paginated([s.to_dict() for s in items], total, page, size)
