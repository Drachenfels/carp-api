import flask

from flask.logging import default_handler

from carp_api import api_request, misc_helper

from . import default


def create_app(
        first_setup=None, setup=None, register_auth=None,
        register_error_handlers=None, register_extra_error_handlers=None,
        register_loggers=None, before_routes=None, register_routes=None,
        final_setup=None):

    from simple_settings import settings

    app = flask.Flask(settings.APP_NAME)

    app.config.from_object(settings.FLASK_DEFAULTS)

    if first_setup:
        first_setup(settings, app)

    app.logger.removeHandler(default_handler)

    setup = setup if setup else default.setup

    setup(settings, app, api_request.ApiRequest)

    register_auth = register_auth if register_auth else default.register_auth

    register_auth(app)

    register_error_handlers = register_error_handlers if \
        register_error_handlers else default.register_error_handlers

    register_error_handlers(app, misc_helper.cors_headers)

    if register_extra_error_handlers:
        register_extra_error_handlers(app)

    register_loggers = register_loggers if register_loggers else \
        default.register_loggers

    register_loggers(settings, app)

    if before_routes:
        before_routes(settings, app)

    register_routes = register_routes if register_routes else \
        default.register_routes

    register_routes(settings, app)

    if final_setup:
        final_setup(settings, app)

    return app
