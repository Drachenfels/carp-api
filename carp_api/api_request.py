import url2vapi

from flask import Request


class ApiRequest(Request):
    '''Extended flask request, notable change: it is version aware.
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.api_request = url2vapi.split(
            self.url, pattern="<version:double>")

    def __str__(self):
        return '<ApiRequest(version={}, url={})>'.format(
            self.api_request.version, self.api_request.remainder)

    @property
    def version(self):
        return self.api_request.version['value'] \
            if self.api_request.version else None

    @property
    def remainder(self):
        return self.api_request.remainder

    def request_is_versioned(self, path):
        '''Determines whether the request URI is versioned'''
        return self.version is not None

    @property
    def person(self):
        return {
            'id': self.user.uid,
            'username': self.user.name,
            'email': self.user.email,
        }

    @property
    def rollbar_person(self):  # pragma: no cover
        """Example intergration with rollbar.

        As per rollbar requirements:
            * id - required
            * username is optiona string
            * email is optional string

        NOTE: any other value will be ignored by rollbar, thus we can add more
        data into `person` property, but narrow it down for forllbar.
        """
        return {
            'id': self.person['uid'],
            'username': self.person['username'],
            'email': self.person['email'],
        }
