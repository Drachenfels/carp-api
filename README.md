# CarpApi

## What is CarpApi

Project is extension of Flask. Main goal is to simplify creation of restful
api's. On high level carp-api is just standard flask app with a few additional
features on top of it:

 * endpoints are grouped into namespaces and namespaces use versioning (ie. we
   can have /1.0/user/create/ and /1.1/user/create/)
 * endpoints are automatically propagated to every version that we have
 * endpoints can override any existing endpoint from given version up
 * input/output normalisation is provided by python-schema that will allow
   normalisation, validation and error handling
 * support of open-api standard generation based on defined endpoints (TODO)
 * error handling is configured out-of-box (TODO)
 * user session and loggers are initially configured and easy to de-stub

## Why CarpApi

It's answer to CRUD principle, carp-api helps you create any api that
creates, amends, removes or picks resources (alternatively craft, alter,
recover and pillage)

## Installation

Via pypi:

    `pip install carp-api`

Or from source code:

    `pip install -e git+git@github.com:Drachenfels/carp-api.git#egg=carp_api`

You are ready to roll!

## Usage

### Note about mandatory variables

Framework wraps around a standard Flask application and documentation for Flask
can be consulted. The main variable FLASK_APP is already preconfigured and set
to `carp_api.server_factory.server_factory:create_app`. For most cases it's
good enough and server_factory allows to override any and all components it
uses to build an application. Another variable is SIMPLE_SETTINGS that defaults
to `carp_api.settings.base` and should be replaced with project specific
settings file. Also all the variables typically exposed by Flask can be
overriden via settings module.

### First run

After successful installation new command will be available in shell
`carp_api`. This is a wrapper around flask with additional checks and defaults
set. For example standard flask would be `flask run` vs `carp_api run` or
`flask routes` is replaced with `carp_api routes`.

Run:

    `carp_api run`

Open base api in a browser by typing:

    `sensible-browser http://localhost:5000`

On default 3 endpoints are present /ping, /favicon.ico and / that returns list
of all available endpoints.

### Adding more endpoints

Assuming for versions 1.0 we want to add capaibilities to create a user, get
list of all users and details about specific user, it would look like as follows.

In version 1.1 we want to add addresses that can be created for given user,
altered and removed from user, while obtaining user details should return
additional information. Also address deletion is considered dangerous and we do
not want it to propagate to any future version.

In version 1.2 we want to add tags creation and deletion.

End effect all available urls will be as follows:

```
    /1.0/user/ (POST) - creates a new user
    /1.0/user/ (GET) - get list of users
    /1.0/user/uid/<uid>/ (GET) - get specific user

    /1.1/user/ (POST) - creates a new user
    /1.1/user/ (GET) - get list of users
    /1.1/user/uid/<uid>/ (GET) - get specific user with address
    /1.1/user/uid/<uid>/address/ (POST) - create address for specific user
    /1.1/user/uid/<uid>/address/uid/<uid>/ (PUT) - alter existing address
    /1.1/user/uid/<uid>/address/<uid>/ (DELETE) - remove address

    /1.2/tag/ (POST) - create a tag
    /1.2/tag/ (GET) - get a tag
    /1.2/user/ (POST) - creates a new user
    /1.2/user/ (GET) - get list of users
    /1.2/user/uid/<uid>/ (GET) - get specific user with address
    /1.2/user/uid/<uid>/address/ (POST) - create address for specific user
    /1.2/user/uid/<uid>/address/uid/<uid>/ (PUT) - alter existing address
```

First inside of your project (let's call it `my_api`) create file `routing.py`,
it should contain following code:

```
    from carp_api.routing import router

    from my_api import endpoints

    # version can be either, tuple, string or float number
    router.enable('1.0', 'user', endpoints=[
        endpoints.CreateUser,
        endpoints.GetListOfUsers,
    ])

    # we can keep enabling as many times as we like in non specific order
    # also version if provided as tuple may be build using strings or digits
    router.enable((1, '0'), 'user', endpoints=[
        endpoints.GetUserByPk,
    ])

    # this will override GetUserByPk from previous version
    router.enable('1.1', 'user', endpoints=[
        endpoints.GetUserWithAddressByPk,
    ])

    # namespace user/address will have no effect on url building
    router.enable('1.1', 'user/address', endpoints=[
        endpoints.CreateUserAddress,
        endpoints.ChangeUserAddress,
        endpoints.DeleteUserAddress,
    ])

    # enable version 1.2 that will have some additional functionality in form of
    # tags
    router.enable('1.2', 'tag', endpoints=[
        endpoints.CreateTag,
        endpoints.GetListOfTags,
    ])
```

Then in a file `endpoints.py`

```
    from carp_api.endpoint import BaseEndpoint


    class CreateUser(BaseEndpoint):
        url = '/'

        methods = ['POST']


    class GetListOfUsers(BaseEndpoint):
        url = '/'


    class GetUserByPk(BaseEndpoint):
        url = '/uid/<id>'

        # add custom name to the endpoint to make easier override with another
        # class
        name = 'GetUserByPk'


    class CreateUserAddress(BaseEndpoint):
        url = '/'

        methods = ['POST']

        @classmethod
        def get_final_url(cls, version, namespace, host=None):
            # method will override default url building
            return '/user/uid/<id>/address/'


    class ChangeUserAddress(BaseEndpoint):
        url = '/'

        methods = ['PUT']

        @classmethod
        def get_final_url(cls, version, namespace, host=None):
            # method will override default url building
            return '/user/uid/<id>/address/uid/<id>/'


    class DeleteUserAddress(BaseEndpoint):
        url = '/'

        methods = ['DELETE']

        # we do not want endpoint to go into future versions
        propagate = False


    class GetUserWithAddressByPk(GetUserByPk):
        url = '/uid/<id>/'


    class CreateTag(BaseEndpoint):
        url = '/'

        methods = ['POST']


    class GetListOfTags(BaseEndpoint):
        url = '/'
```

Finally we will need to create project specific settings `my_api/settings.py`
that will keep following code:

```
    from carp_api.settings.base import *  # NOQA


    CARP_API_ROUTING = 'my_api.routing'
```

Now we can run our project with command: `SIMPLE_SETTINGS=my_api.settings carp_api run`

And done, after we launch project it should have all endpoints resolved and
ready to go.

## Sample project ready to clone

Git clone [Carp-Api Sample Project](https://github.com/Drachenfels/carp-api-sample-project)
in order to have local project serving responses.

Planned features for sample project involve:

 * pytest testing endpoints
 * docker containers
 * google app engine ready to use
 * all main features of endpoint creation present
