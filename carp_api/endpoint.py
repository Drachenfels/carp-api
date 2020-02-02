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

    @property
    def short_documentation(self):
        """This will be used to auto-generate short description for a
        self-documentation
        """
        message = (
            "[Endpoint has no docstring nor attribute/property "
            "short_documentation]"
        )

        if not self.__doc__:
            return message

        return self.__doc__.split('\n')[0].strip()

    @property
    def long_documentation(self):
        """This will be used to auto-generate long, description documentation
        for puprose of doc autogeneration.
        """
        message = (
            "[Endpoint has no docstring nor attribute/property "
            "long_documentation]"
        )

        if not self.__doc__:
            return message

        return self.__doc__

    def action(self, *args, **kwargs):  # pylint: disable=unused-argument
        raise exception.EndpointNotImplementedError(
            "Endpoint do not implement action")

    def __str__(self):
        return '<Endpoint name="{}">'.format(self.get_final_name())

    def get_final_name(self):
        return helper.get_endpoint_name(self)

    def get_final_url(self, version, namespace, host=None):
        """Builds final url.

        Because given endpoint may or may not exist in many contexts (aka
        various combination of versions and namespaces) exact url is defined on
        app startup.
        """
        url_instance = url.Url()

        if version:
            url_instance.add(version)

        if namespace:
            url_instance.add(namespace)

        url_instance.add(self.url)

        return url_instance.as_full_url(
            trailing_slash=self.trailing_slash, host=host)

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
