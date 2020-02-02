APP_NAME = 'carp_api'

DEBUG = False

TESTING = False

ENV = 'production'

# define module that should perform namespace/endpoint registration, this
# module will be loaded before server start
CARP_API_ROUTING = None

# common routes are defined by base carp-api and it's limited to list of all
# endpoints, ping and favicon, in case you do not need them set to False
ROUTING_ADD_COMMON = True

# app shutdown route is useful for old test frameworks like a nosetest, it
# exposes additional route that will kill the running server app, because it's
# potentially disrupting it has own setting
#
# NOTE: it's recommended to use newer test frameworks like pytest that support
# context allowing to start and shutdown the server at the begining of the
# test
ROUTING_ADD_SHUTDOWN_ROUTE = False

# if you have two applications using same server/domain ie. example.com,
# session will be distinguished using APP_NAME so that session_cookies on a
# browser won't get messed up with different users working on same session
SESSION_NAMESPACE = APP_NAME

DEFAULT_LANGUAGE_CODE = 'en_GB'
DEFAULT_TIMEZONE = 'UTC'

# logging is handled by standard `python` logging module, hence this
# dictionary, it is used by logging.config.dictConfig on app start-up,
# after that there is possibility to register new handlers with any number of
# existing loggers
# NOTE: for more complex solution, `create_app` accepts argument
# `register_loggers` that will completely override LOGGING configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'class': 'logging.Formatter',
            'format': '%(asctime)s %(levelname)s %(name)s %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'standard',
        },
    },
    'loggers': {
        'carp_api': {
            'handlers': ['console'],
        },
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['console'],
    },
}


# if you want to register additional handlers for loging as defined in LOGGING
# dict, override LOGGING_ADDITIONAL_HANDLERS with list of callables that
# take no arguments and return instance of handler, ie.
# LOGGING_ADDITIONAL_HANDLERS = [lambda: SMTPHandler()]
LOGGING_ADDITIONAL_HANDLERS = ()

# if you want to attach extra handlers defined in LOGGING_ADDITIONAL_HANDLERS,
# override LOGGING_ADDITIONAL_LOGGERS with list of strings, where each of them
# defines logger that should have handler added, ie. sqlalchemy
# note: 'app.logger' is standard flask logger
LOGGING_ADDITIONAL_LOGGERS = (
    'app.logger',
)

FLASK_SERVER_HOST = '0.0.0.0'
FLASK_SERVER_PORT = 5000

# FLASK_DEFAULTS is used by server_factory:create_app, change if you
# want to use different defaults than listed in flask_defaults
FLASK_DEFAULTS = 'carp_api.settings.flask_defaults'
