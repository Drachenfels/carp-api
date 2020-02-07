import flask
import python_schema

from carp_api import exception, url, request_parser, misc_helper
from carp_api.routing import helper


class BaseEndpoint:
    # if set to None, will default to GET, HEAD and OPTIONS
    methods = ['GET', 'OPTIONS']

    # if set, given object will be constructed on entry
    input_schema = None

    # if set, given object will be returned
    output_schema = None

    # under which url this endpoint should be available ie user or user/details
    url = None

    # if set given permission will be checked before attempting to call
    # endpoint
    permissions = ()

    # if should move to next version (if and when there is next version)
    propagate = True

    # if we want to add a trailing slash, follows:
    # https://flask.palletsprojects.com/en/1.1.x/quickstart/#unique-urls-redirection-behavior
    trailing_slash = True

    # override if given endpoint should return different http code than what
    # http_codes_map will pick
    http_code = None

    http_codes_map = {
        'GET': 200,
        'HEAD': 200,
        'OPTIONS': 200,
        'TRACE': 200,

        'POST': 201,
        'CONNECT': 201,

        'PUT': 202,
        'DELETE': 202,
        'PATCH': 202,
    }

    # Version is set when adding an instance of the endpoint to the Flask app
    _version = None

    # Namespace is set when adding an instance of the enpoint to the Flask app
    _namespace = None

    def get_short_documentation(self):
        """Method used to generate short, one line description what endpoints
        does.
        """
        return (
            "[Endpoint does not implement method get_short_documentation]"
        )

    def get_long_documentation(self):
        """Method used to generate content rich documentation ie. open-api
        machinery.
        """
        return (
            "[Endpoint does not implement method get_long_documentation]"
        )

    def action(self, *args, **kwargs):  # pylint: disable=unused-argument
        raise exception.EndpointNotImplementedError(
            "Endpoint do not implement action")

    def __str__(self):
        return '<Endpoint name="{}">'.format(self.get_final_name())

    def get_final_name(self):
        return helper.get_endpoint_name(self)

    def get_final_url(self, host=None):
        """Builds final url.

        Because given endpoint may or may not exist in many contexts (aka
        various combination of versions and namespaces) exact url is defined on
        app startup.
        """
        url_instance = url.Url()

        if self.get_version():
            url_instance.add(self.get_version())

        if self.get_namespace():
            url_instance.add(self.get_namespace())

        url_instance.add(self.url)

        return url_instance.as_full_url(
            trailing_slash=self.trailing_slash, host=host)

    def set_namespace(self, namespace):
        """Method is called shortly before enpoint is registered with Flask.

        Used old-school setter/getter approach in order to make it easier to
        customise behaviour of the framework for specific use cases.
        """
        self._namespace = namespace

    def get_namespace(self):
        return self._namespace

    def set_version(self, version):
        """Method is called shortly before enpoint is registered with Flask.

        Used old-school setter/getter approach in order to make it easier to
        customise behaviour of the framework for specific use cases.
        """
        self._version = version

    def get_version(self):
        return self._version

    @property
    def request(self):
        return flask.request

    def __eq__(self, other):
        return isinstance(other, BaseEndpoint) and \
            self.get_final_name() == other.get_final_name()

    def parse_input(self, payload, args, kwargs):
        """Convert payload into schema and then make it first argument on args
        list.
        """
        instance = self.input_schema()  # pylint: disable=not-callable

        try:
            instance.loads(payload)
        except python_schema.exception.PayloadError as err:
            raise exception.PayloadError(err)

        return [instance] + args, kwargs

    def parse_output(self, payload):
        instance = self.output_schema()  # pylint: disable=not-callable

        try:
            instance.loads(payload)

        except python_schema.exception.PayloadError as err:
            raise exception.ResponseContentError(err)

        return instance.dumps()  # in future add ctx={'user': request.user}

    def get_payload(self):
        content_type = self.request.headers.get('Content-Type', '')

        if 'application/json' in content_type:
            return self.request.get_json()

        return request_parser.form_to_python(self.request.values)

    def pre_action(self):
        """Override if you want to manipulate payload before it goes to
        input_schema parsing
        """
        return

    def post_action(self, response):
        """Override if you want to manipulate result before it goes back to
        the user
        """
        if not isinstance(response, flask.wrappers.Response):
            response = flask.make_response(flask.jsonify(response))

        response.status_code = self.http_code if self.http_code else \
            self.http_codes_map.get(self.request.method, 200)

        response = self.add_cors(response)

        return response

    def add_cors(self, response):
        """Method adds cors headers, override if you want to prevent it for
        your endpoint.
        """
        response.headers.extend(misc_helper.cors_headers())

        return response

    def __call__(self, *args, **kwargs):
        if self.request.method == 'OPTIONS':
            result = flask.current_app.make_default_options_response()
        else:
            self.pre_action()

            payload = self.get_payload()

            if self.input_schema:
                args, kwargs = self.parse_input(payload, args, kwargs)

            # pylint: disable=assignment-from-no-return
            result = self.action(*args, **kwargs)
            # pylint: enable=assignment-from-no-return

            if self.output_schema:
                result = self.parse_output(result)

        result = self.post_action(result)

        return result
