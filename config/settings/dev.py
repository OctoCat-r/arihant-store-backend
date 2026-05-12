from .base import *  # noqa: F403, F401
import certifi
import mongoengine

MONGO_URI = os.getenv('MONGO_URI')  # noqa: F405
MONGO_DB = os.getenv('MONGO_DB', 'arihant_db')  # noqa: F405

if MONGO_URI:
    mongoengine.connect(db=MONGO_DB, host=MONGO_URI, tlsCAFile=certifi.where())
else:
    # Local dev: individual settings
    MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')  # noqa: F405
    MONGO_PORT = int(os.getenv('MONGO_PORT', '27017'))  # noqa: F405
    MONGO_USERNAME = os.getenv('MONGO_USERNAME')  # noqa: F405
    MONGO_PASSWORD = os.getenv('MONGO_PASSWORD')  # noqa: F405

    connect_kwargs = dict(db=MONGO_DB, host=MONGO_HOST, port=MONGO_PORT)
    if MONGO_USERNAME and MONGO_PASSWORD:
        connect_kwargs['username'] = MONGO_USERNAME
        connect_kwargs['password'] = MONGO_PASSWORD
    mongoengine.connect(**connect_kwargs)
