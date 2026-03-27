import os
import logging


def load_bool(env_key, default=True):
    var = os.environ.get(env_key, str(default))
    return var.lower() in {'true', 'y', '1', 'yes'}


HOST = os.environ.get('MESSAGING_HOST', '0.0.0.0')
PORT = int(os.environ.get('MESSAGING_PORT', 5001))
UVICORN_WORKERS = int(os.environ.get('MESSAGING_UVICORN_WORKERS', 2))
DEBUG = load_bool('MESSAGING_DEBUG')

CORE_URL = os.environ.get('CORE_URL', 'http://localhost:8000').rstrip('/')

log_level = os.environ.get('LOG_LEVEL', 'INFO')
if log_level == 'INFO':
    LOG_LEVEL = logging.INFO
else:
    LOG_LEVEL = logging.DEBUG

LOG_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'base_format': {
            '()': 'uvicorn.logging.DefaultFormatter',
            'format': '%(asctime)s %(levelname)s %(module)s:%(lineno)d '
            '%(funcName)s[%(process)d.%(threadName)s] %(message)s',
            'datefmt': '%a %b %d %H:%M:%S%z %Y',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'base_format',
        },
        'uvicorn_error_handler': {
            'level': 'ERROR',
            'formatter': 'base_format',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 16777216,
            'filename': 'log/error.log',
        },
        'uvicorn_access_handler': {
            'level': 'DEBUG',
            'formatter': 'base_format',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 16777216,
            'filename': 'log/access.log',
        },
        'messaging_service': {
            'level': 'DEBUG',
            'formatter': 'base_format',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 16777216,
            'filename': 'log/messages.log',
        },
    },
    'loggers': {
        'uvicorn': {
            'handlers': ['messaging_service', 'uvicorn_error_handler'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
        'uvicorn.access': {
            'handlers': ['uvicorn_access_handler'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
        'messaging_service': {
            'handlers': ['messaging_service'],
            'level': LOG_LEVEL
        },
    },
}

if DEBUG:
    for logger in LOG_CONFIG['loggers'].values():
        logger['handlers'].append('console')
