from rest_framework.response import Response


def ok(data, status=200):
    return Response({'ok': True, 'data': data}, status=status)


def paginated(data, total, page, page_size):
    return Response({
        'ok': True,
        'data': data,
        'meta': {'total': total, 'page': page, 'page_size': page_size},
    })


def err(message, status=400):
    return Response({'ok': False, 'error': message}, status=status)
