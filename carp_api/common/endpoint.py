import pathlib

from flask import request, current_app, make_response

from carp_api import endpoint, signal

from carp_api.common import logic


class Ping(endpoint.BaseEndpoint):
    """Ping to get response: "pong".

    Used for health check.
    """
    url = 'ping'
    name = 'ping'

    def action(self):  # pylint: disable=arguments-differ
        resp = logic.get_pong(request.version)

        return resp


class UrlMap(endpoint.BaseEndpoint):
    """All urls available on api.
    """
    url = ''
    name = 'url_map'

    # output_schema = output_schema.Map

    def action(self):  # pylint: disable=arguments-differ
        func_list = logic.get_url_map(request.version)

        return func_list


class ShutDown(endpoint.BaseEndpoint):
    """ShutDown rouote, that terminates the server, expose it only for
    development and testing environment, unless you like server restarts.
    """
    url = 'shutdown'
    name = 'shutdown'

    methods = ['POST']

    def action(self):  # pylint: disable=arguments-differ
        func = request.environ.get('werkzeug.server.shutdown')

        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')

        # pylint: disable=protected-access
        signal.app_shutdown.send(current_app._get_current_object())
        # pylint: enable=protected-access

        func()


class FavIcon(endpoint.BaseEndpoint):
    """Favicon, to prevent 500 when other favicons are unavailable.
    """
    url = 'favicon.ico'
    name = 'favicon'

    trailing_slash = False

    propagate = False

    def action(self):  # pylint: disable=arguments-differ
        file_path = (
            pathlib.PosixPath(__file__).parent.parent.absolute() / 'data' /
            'favicon.png'
        )

        with open(file_path, 'rb') as fpl:
            resp = make_response(fpl.read())

        resp.headers['content-type'] = 'image/vnd.microsoft.icon'

        return resp
