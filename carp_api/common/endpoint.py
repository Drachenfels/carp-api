import pathlib
import json

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

    def get_short_documentation(self):
        version = self.get_version()

        if version:
            return f'Returns pong if version {version} is working'

        return f'Returns pong'

    def get_long_documentation(self):
        return self.get_short_documentation()


class UrlMap(endpoint.BaseEndpoint):
    """All urls available on api.
    """
    url = ''
    name = 'url_map'

    def action(self):  # pylint: disable=arguments-differ
        result = logic.get_url_map(request.version)

        return make_response(
            json.dumps(result), 200, {'Content-Type': 'application/json'})

    def get_short_documentation(self):
        version = self.get_version()

        if version:
            return f'Returns list of urls for version {version}'

        return f'Returns list of all urls'

    def get_long_documentation(self):
        return self.get_short_documentation()


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

    def get_short_documentation(self):
        return 'Responds with .png favicon for a project.'

    def get_long_documentation(self):
        return (
            'Responds with .png favicon for a project. Useful when api is '
            'opened with a browser. It will trigger favicon call in the '
            'background.'
        )


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
        signal.app_shutdown.send(current_app._get_current_object())  # NOQA
        # pylint: enable=protected-access

        func()
