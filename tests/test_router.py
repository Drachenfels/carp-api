import pytest

from carp_api import exception
from carp_api.routing import component, router
from carp_api.endpoint import BaseEndpoint


class SimpleEndpoint(BaseEndpoint):
    url = '/'


@pytest.fixture
def reset_state_of_router():
    old_versions = router.Router.versions
    router.Router.versions = component.VersionList()
    yield
    router.Router.versions = old_versions


def test_basic_routing(reset_state_of_router):
    router.enable('1.0', 'user', endpoints=[
        SimpleEndpoint
    ])

    version = router.Router.versions[0]

    assert version.as_str() == '1.0'
    assert len(version) == 1
    assert version.has('user') is True
    assert version.get('user').has(SimpleEndpoint) is True


def test_that_we_cannot_register_same_endpoint_twice(reset_state_of_router):
    router.enable('1.0', 'user', endpoints=[
        SimpleEndpoint
    ])

    with pytest.raises(exception.DuplicateEndpointError):
        router.enable('1.0', 'user', endpoints=[
            SimpleEndpoint
        ])


def test_we_can_register_endpoint_without_version(reset_state_of_router):
    router.enable(namespace='user', endpoints=[
        SimpleEndpoint
    ])

    version = router.Router.versions[0]

    assert version.as_str() == ''
    assert len(version) == 1
    assert version.has('user') is True
    assert version.get('user').has(SimpleEndpoint)


def test_we_can_register_endpoint_without_namespace(reset_state_of_router):
    router.enable(version=1.0, endpoints=[
        SimpleEndpoint
    ])

    version = router.Router.versions[0]

    assert version.as_str() == '1.0'
    assert len(version) == 1
    assert version.has('') is True
    assert version.get('').has(SimpleEndpoint)


def test_we_can_register_endpoint_without_namespace_and_version(
        reset_state_of_router):
    router.enable(endpoints=[SimpleEndpoint])

    version = router.Router.versions[0]

    assert version.as_str() == ''
    assert len(version) == 1
    assert version.has('') is True
    assert version.get('').has(SimpleEndpoint)


def test_we_can_register_same_endpoint_twice_at_different_namespaces(
        reset_state_of_router):
    router.enable('1.0', 'user', endpoints=[SimpleEndpoint])
    router.enable('1.0', 'vehicle', endpoints=[SimpleEndpoint])

    version = router.Router.versions[0]

    assert version.as_str() == '1.0'
    assert len(version) == 2
    assert version.has('user') is True
    assert version.has('vehicle') is True

    assert version.get('user').has(SimpleEndpoint)
    assert version.get('vehicle').has(SimpleEndpoint)


def test_we_can_override_endpoint_at_will(reset_state_of_router):
    class BetterSimpleEndpoint(BaseEndpoint):
        url = '/'

    router.enable('1.0', 'user', endpoints=[
        SimpleEndpoint
    ])

    router.enable('1.1', 'user', endpoints=[
        BetterSimpleEndpoint
    ])

    version = router.Router.versions[0]

    assert version.as_str() == '1.0'
    assert len(version) == 1
    assert version.has('user') is True
    assert version.get('user').has(SimpleEndpoint)

    version = router.Router.versions[1]

    assert version.as_str() == '1.1'
    assert len(version) == 1
    assert version.has('user') is True
    assert version.get('user').has(BetterSimpleEndpoint)
