PROJECT = 'quiverweb'

LOCALE = 'en_US'

PROCESSES = 1

PORT = 8000

DEBUG = True

MONGODB_URI = 'mongodb://localhost:27017'
MONGODB_NAME = 'quiverweb'

LOGGERS = {
    '': {
        'level': 'INFO',
        'fmt': '%(color)s[%(fixed_levelname)s %(asctime)s %(module)s:%(lineno)d]%(end_color)s %(message)s',
        #'fmt': '[%(fixed_levelname)s %(asctime)s %(module)s:%(lineno)d] %(message)s',
        'datefmt': '%Y-%m-%d %H:%M:%S',
    }
}

LOG_REQUEST = True

LOG_RESPONSE = False

TIME_ZONE = 'Asia/Shanghai'

STATIC_PATH = 'static'

TEMPLATE_PATH = 'template'

# You can use jinja2 instead
TEMPLATE_ENGINE = 'tornado'

LOGGING_IGNORE_URLS = [
    '/favicon.ico',
]
