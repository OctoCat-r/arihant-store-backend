from .base import *  # noqa: F403, F401
import certifi
import mongoengine

# Production always uses Atlas URI — fail loudly if missing
MONGO_URI = os.environ['MONGO_URI']  # noqa: F405
MONGO_DB = os.getenv('MONGO_DB', 'arihant_db')  # noqa: F405

mongoengine.connect(db=MONGO_DB, host=MONGO_URI, tlsCAFile=certifi.where())

# Security hardening
DEBUG = False
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = False  # Railway/Render handle HTTPS termination upstream
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

STATIC_ROOT = BASE_DIR / 'staticfiles'  # noqa: F405
