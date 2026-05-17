import time

_store: dict = {}


def get(key: str, ttl: float):
    entry = _store.get(key)
    if entry and time.monotonic() - entry['ts'] < ttl:
        return entry['data']
    return None


def put(key: str, data) -> None:
    _store[key] = {'data': data, 'ts': time.monotonic()}


def delete(key: str) -> None:
    _store.pop(key, None)


def delete_prefix(prefix: str) -> None:
    for k in [k for k in _store if k.startswith(prefix)]:
        del _store[k]
