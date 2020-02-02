"""Check that building and resolving namespaces with endpoints works as
intended.

After configuring endpoints as follows:

    /1.0/user/ (POST) - creates a new user
    /1.0/user/ (GET) - get list of users
    /1.0/user/uid/(id)/ (GET) - get specific user

    /1.1/user/address/user_uid/(id)/ (POST) - create address for specific user
    /1.1/user/address/user_uid/(id)/address/(id)/ (PUT) - alter existing
        address
    /1.1/user/address/user_uid/(id)/address/(id)/ (DELETE) - remove address,
        this enpoint does not propagate
    /1.1/user/uid/(id)/ (GET) - get user with address on (tests overriding)

    /1.2/tag/ (POST) - create a tag
    /1.2/tag/ (GET) - get a tag


It should resolve into this:

    1.0
        -> user
            -> POST /
            -> GET /
            -> GET /uid/(id)

    1.1
        -> user
            -> POST /
            -> GET /
            -> GET /uid/(id)
            -> address
                -> POST /user_uid/(id)/
                -> PUT /user_uid/(id)/address/(id)/
                -> DELETE /user_uid/(id)/address/(id)/

    1.2
        -> user
            -> POST /
            -> GET /
            -> GET /uid/(id)
            -> address
                -> POST /user_uid/(id)/
                -> PUT /user_uid/(id)/address/(id)/
        -> tag
            -> POST /
            -> GET /

"""

import pytest

from carp_api.endpoint import BaseEndpoint
from carp_api.routing import router, component


class CreateUser(BaseEndpoint):
    url = '/'

    methods = ['POST']


class GetListOfUsers(BaseEndpoint):
    url = '/'


class GetUserByPk(BaseEndpoint):
    url = '/uid/<id>'

    name = 'GetUserByPk'


class CreateUserAddress(BaseEndpoint):
    url = '/'

    methods = ['POST']

    @classmethod
    def get_final_url(cls, version, namespace, host=None):
        return '/user/uid/<id>/address/'


class ChangeUserAddress(BaseEndpoint):
    url = '/'

    methods = ['PUT']

    @classmethod
    def get_final_url(cls, version, namespace, host=None):
        return '/user/uid/<id>/address/uid/<id>/'


class DeleteUserAddress(BaseEndpoint):
    url = '/'

    methods = ['DELETE']

    propagate = False


class GetUserWithAddressByPk(GetUserByPk):
    url = '/uid/<id>/'

    name = 'GetUserByPk'


class CreateTag(BaseEndpoint):
    url = '/'

    methods = ['POST']


class GetListOfTags(BaseEndpoint):
    url = '/'


@pytest.fixture
def reset_state_of_router():
    old_versions = router.Router.versions
    router.Router.versions = component.VersionList()
    yield
    router.Router.versions = old_versions


def test_router_will_materialise_url_structure_properly(reset_state_of_router):
    router.enable(1.0, 'user', endpoints=[
        CreateUser,
        GetListOfUsers,
    ])

    # version is a bit abomination but want to check if framework is resiliant
    router.enable((1, '0'), 'user', endpoints=[
        GetUserByPk,
    ])

    router.enable('1.1', 'user', endpoints=[
        GetUserWithAddressByPk,
    ])

    # sub-namespace, thus we add slash, it will have no meaning for url
    # resolving as those endpint will use custom urls
    router.enable('1.1', 'user/address', endpoints=[
        CreateUserAddress,
        ChangeUserAddress,
        DeleteUserAddress,
    ])

    router.enable('1.2', 'tag', endpoints=[
        CreateTag,
        GetListOfTags,
    ])

    final_routing = router.Router.get_final_routing()

    assert final_routing[0].as_str() == '1.0'
    assert len(final_routing[0]) == 1
    assert final_routing[0].has('user') is True
    assert len(final_routing[0].get('user')) == 3
    assert final_routing[0].has('user/address') is False
    assert final_routing[0].has('tag') is False

    assert final_routing[1].as_str() == '1.1'
    assert len(final_routing[1]) == 2
    assert final_routing[1].has('user') is True
    assert len(final_routing[1].get('user')) == 3
    assert final_routing[1].has('user/address') is True
    assert len(final_routing[1].get('user/address')) == 3
    assert final_routing[0].has('tag') is False

    assert final_routing[2].as_str() == '1.2'
    assert len(final_routing[2]) == 3
    assert final_routing[2].has('user') is True
    assert len(final_routing[2].get('user')) == 3
    assert final_routing[2].has('user/address') is True
    assert len(final_routing[2].get('user/address')) == 2
    assert final_routing[2].has('tag') is True
    assert len(final_routing[2].get('tag')) == 2

    list_of_urls = final_routing.as_flat_list()

    assert list_of_urls[0][0] == '1.0'
    assert list_of_urls[0][1] == 'user'

    assert 'CreateUser' in list_of_urls[0][2].keys()
    assert 'GetListOfUsers' in list_of_urls[0][2].keys()
    assert 'GetUserByPk' in list_of_urls[0][2].keys()

    assert list_of_urls[1][0] == '1.1'
    assert list_of_urls[1][1] == 'user'

    assert 'CreateUser' in list_of_urls[1][2].keys()
    assert 'GetListOfUsers' in list_of_urls[1][2].keys()
    assert 'GetUserByPk' in list_of_urls[1][2].keys()

    assert list_of_urls[2][0] == '1.1'
    assert list_of_urls[2][1] == 'user/address'

    assert 'ChangeUserAddress' in list_of_urls[2][2].keys()
    assert 'CreateUserAddress' in list_of_urls[2][2].keys()
    assert 'DeleteUserAddress' in list_of_urls[2][2].keys()

    assert list_of_urls[3][0] == '1.2'
    assert list_of_urls[3][1] == 'tag'

    assert 'CreateTag' in list_of_urls[3][2].keys()
    assert 'GetListOfTags' in list_of_urls[3][2].keys()

    assert list_of_urls[4][0] == '1.2'
    assert list_of_urls[4][1] == 'user'

    assert 'CreateUser' in list_of_urls[4][2].keys()
    assert 'GetListOfUsers' in list_of_urls[4][2].keys()
    assert 'GetUserByPk' in list_of_urls[4][2].keys()

    assert list_of_urls[5][0] == '1.2'
    assert list_of_urls[5][1] == 'user/address'

    assert 'ChangeUserAddress' in list_of_urls[5][2].keys()
    assert 'CreateUserAddress' in list_of_urls[5][2].keys()
