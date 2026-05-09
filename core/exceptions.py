from rest_framework.views import exception_handler
from rest_framework.response import Response


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        detail = response.data.get('detail', str(response.data))
        response.data = {'ok': False, 'error': str(detail)}
    return response
