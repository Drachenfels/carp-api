import importlib
import logging

import flask

from carp_api import exception


def setup(settings, app, request_class):
    """Setup is perfomred early and for certain before first request is
    handled.
    """
    @app.before_first_request
    def before_first_request():  # pylint: disable=unused-variable
        pass

    @app.before_request
    def example_preprocessor():  # pylint: disable=unused-variable
        pass

    @app.after_request
    def after_request(resp):  # pylint: disable=unused-variable
        """If there is anything that api should do before ending request, add
        it in here for example you might have transactional backend that
        require commit or rollback at the end of each request.

        NOTE: if unhandled exception happens, this function is not going to be
        executed.
        """
        return resp

    app.debug = settings.DEBUG

    # custom request class in case you need more functionality than what Flask
    # offers
    app.request_class = request_class


def register_auth(app):
    """On default application will attach unauthorised user. Override function
    if you want anything smarter than that"""
    from carp_api.auth_model import UnauthorizedUser

    @app.before_request
    def user_auth():  # pylint: disable=unused-variable
        flask.request.user = UnauthorizedUser()


def _make_response(message, code):
    resp = flask.make_response(message)

    resp.status_code = code

    return resp


def _add_cors(response, cors_headers):
    response.headers.extend(cors_headers())

    return response


def register_error_handlers(app, cors_headers):
    @app.errorhandler(exception.NotFoundError)
    def handle_missing_asset(err):  # pylint: disable=unused-variable
        """When we request asset but it's not found, ie. /user/uid/1/ should
        return user but there is no user for uid 1.
        """
        response = _make_response(str(err), err.http_code)

        return _add_cors(response, cors_headers)

    @app.errorhandler(exception.EndpointNotImplementedError)
    def handle_missing_implementation(err):  # pylint: disable=unused-variable
        """When endpoint was defined but it's content is empty.
        """
        app.logger.error(err, exc_info=True)

        response = _make_response(str(err), err.http_code)

        return _add_cors(response, cors_headers)

    @app.errorhandler(exception.BasePayloadError)
    def handle_malformed_input(err):  # pylint: disable=unused-variable
        """When incoming data is one way or another malformed, ie. missing
        key, wrong type or field that is not expected for given endpoint.
        """
        app.logger.error(err, exc_info=True)

        response = _make_response(str(err), err.http_code)

        return _add_cors(response, cors_headers)

    @app.errorhandler(exception.ValidationError)
    def handle_invalid_input(err):  # pylint: disable=unused-variable
        """When incoming data is valid in structure and thus has passed
        handle_malformed_input check, but is not avalid, ie. client_id
        has to be positive integer or email needs to have '@'
        """
        app.logger.error(err, exc_info=True)

        response = flask.jsonify(err.messages)
        response.status_code = err.http_code
        response.headers['Content-Type'] = 'application/json'

        return _add_cors(response, cors_headers)

    @app.errorhandler(exception.AccessForbidden)
    def access_forbidden(err):  # pylint: disable=unused-variable
        app.logger.info(err, exc_info=True)

        response = _make_response(
            "Access forbidden ({})".format(str(err)), err.http_code)

        return _add_cors(response, cors_headers)

    @app.errorhandler(exception.ResponseError)
    def handle_invalid_response(err):  # pylint: disable=unused-variable
        """When application handled incoming data, but according to definition
        of endpoint response data makes little to no sense. Usually happens
        when schema is stale or business logic has changed recently.
        """
        app.logger.error(err, exc_info=True)

        response = flask.jsonify(err.messages)
        response.status_code = err.http_code
        response.headers['Content-Type'] = 'application/json'

        return _add_cors(response, cors_headers)

    @app.errorhandler(exception.Unauthorised)
    def unauthorised(err):  # pylint: disable=unused-variable
        app.logger.info(err, exc_info=True)

        response = _make_response("Unauthorsed", err.http_code)

        return _add_cors(response, cors_headers)

    @app.errorhandler(exception.CarpApiException)
    def handle_unrecognised_exception(err):  # pylint: disable=unused-variable
        app.logger.error(err, exc_info=True)

        response = _make_response(str(err), err.http_code)

        return _add_cors(response, cors_headers)

    @app.errorhandler(404)
    def _handle_404(err):  # pylint: disable=unused-argument
        response = _make_response("URL - not found!", 404)

        return _add_cors(response, cors_headers)

    @app.errorhandler(405)
    def _handle_405(err):  # pylint: disable=unused-argument
        response = _make_response("URL found but METHOD not supported", 405)

        return _add_cors(response, cors_headers)

    @app.errorhandler(Exception)
    def handle_remaining_errors(err):  # pylint: disable=unused-variable
        """Handler for everything else that is not defined above
        """
        app.logger.error(err, exc_info=True)

        response = _make_response(str(err), 500)

        return _add_cors(response, cors_headers)

    # NOTE: add inactive version handling?
    # except exc.InactiveAPIVersion as err:
    #     return tool.responses.error_response(
    #       'Inactive API version', 404), ''


def register_routes(settings, app):
    from carp_api.routing import router

    if settings.ROUTING_ADD_COMMON:
        from carp_api.common import endpoint

        router.enable(None, '', [
            endpoint.Ping,
            endpoint.UrlMap,
            endpoint.FavIcon,
        ])

    if settings.ROUTING_ADD_SHUTDOWN_ROUTE:
        from carp_api.common import endpoint

        router.enable(None, '', [
            endpoint.ShutDown,
        ])

    if settings.CARP_API_ROUTING:
        importlib.import_module(settings.CARP_API_ROUTING)

    final_routing = router.Router.get_final_routing().as_flat_list()

    # because each endpoint can force custom url lets check if given endpoint
    # was not already registered by something else. Otherwise first one is
    # getting through the post and it leads to ambiguity.
    final_urls = {}

    for version, namespace, endpoints in final_routing:
        for name, instance in endpoints.items():
            if isinstance(instance, type):
                instance = instance()

            new_url = instance.get_final_url(version, namespace)

            if new_url in final_urls.keys():
                raise exception.ConflictingUrlsError(
                    "Url was already registered by {name}".format(
                        name=final_urls[new_url]
                    )
                )

            final_urls[new_url] = instance.get_final_name()

            app.add_url_rule(
                new_url, name, instance
            )


def register_loggers(settings, app):
    logging.config.dictConfig(settings.LOGGING)

    if settings.LOGGING_ADDITIONAL_HANDLERS:
        handlers = [
            get_handler()
            for get_handler in settings.LOGGING_ADDITIONAL_HANDLERS]
        loggers = [
            app.loger if name == 'app.logger' else logging.getLogger(name)
            for name in settings.LOGGING_ADDITIONAL_LOGGERS]

        for logger in loggers:
            for handler in handlers:
                logger.addHandler(handler)
