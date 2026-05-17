import logging
import traceback
from rest_framework.views import exception_handler
from rest_framework.response import Response

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    view = context.get('view')
    request = context.get('request')

    response = exception_handler(exc, context)

    if response is not None:
        # Known DRF exception — normalise shape
        detail = response.data.get('detail', str(response.data))
        response.data = {'ok': False, 'error': str(detail)}
        return response

    # Unhandled exception — log the full traceback and return 500
    logger.error(
        'Unhandled exception in %s %s\n%s',
        getattr(request, 'method', '?'),
        getattr(request, 'path', '?'),
        traceback.format_exc(),
        exc_info=exc,
    )
    return Response(
        {'ok': False, 'error': 'Internal server error.', 'detail': str(exc)},
        status=500,
    )
