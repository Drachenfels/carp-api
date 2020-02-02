import pytest

from carp_api import exception

from carp_api.routing import helper, component


def test_normalisations_that_should_work():
    normalised_version = helper.normalise_version(None)

    assert normalised_version == (-1, -1, -1)

    normalised_version = helper.normalise_version(0)

    assert normalised_version == (0, -1, -1)

    normalised_version = helper.normalise_version('')

    assert normalised_version == (-1, -1, -1)

    normalised_version = helper.normalise_version(1)

    assert normalised_version == (1, -1, -1)

    normalised_version = helper.normalise_version(2)

    assert normalised_version == (2, -1, -1)

    normalised_version = helper.normalise_version(0.)

    assert normalised_version == (0, 0, -1)

    normalised_version = helper.normalise_version(0.0)

    assert normalised_version == (0, 0, -1)

    normalised_version = helper.normalise_version(1.0)

    assert normalised_version == (1, 0, -1)

    normalised_version = helper.normalise_version(1.1)

    assert normalised_version == (1, 1, -1)

    normalised_version = helper.normalise_version(2.1)

    assert normalised_version == (2, 1, -1)

    normalised_version = helper.normalise_version('1.1.2')

    assert normalised_version == (1, 1, 2)

    normalised_version = helper.normalise_version('2.1.2')

    assert normalised_version == (2, 1, 2)

    normalised_version = helper.normalise_version('0.1')

    assert normalised_version == (0, 1, -1)

    normalised_version = helper.normalise_version('1.1')

    assert normalised_version == (1, 1, -1)

    normalised_version = helper.normalise_version('2.1')

    assert normalised_version == (2, 1, -1)

    normalised_version = helper.normalise_version('1')

    assert normalised_version == (1, -1, -1)

    normalised_version = helper.normalise_version('2')

    assert normalised_version == (2, -1, -1)

    normalised_version = helper.normalise_version((1, 1, 1))

    assert normalised_version == (1, 1, 1)

    normalised_version = helper.normalise_version((1, 2, 1))

    assert normalised_version == (1, 2, 1)

    normalised_version = helper.normalise_version((0, 0, 0))

    assert normalised_version == (0, 0, 0)

    normalised_version = helper.normalise_version(('1', '2', '3'))

    assert normalised_version == (1, 2, 3)

    normalised_version = helper.normalise_version((1,))

    assert normalised_version == (1, -1, -1)

    normalised_version = helper.normalise_version(None, 6)

    assert normalised_version == (-1, -1, -1, -1, -1, -1)


def test_normalisations_that_should_fail():
    with pytest.raises(exception.RoutingConfigurationError):
        helper.normalise_version(('1.1', '1'))

    with pytest.raises(exception.RoutingConfigurationError):
        helper.normalise_version((1, None))

    with pytest.raises(exception.RoutingConfigurationError):
        helper.normalise_version((1, -1, 1))


def test_operations_on_version_list_are_working():
    val = component.VersionList()

    val.get_or_create_version((3, -1, -1))
    val.get_or_create_version((4, -1, -1))
    val.get_or_create_version((1, -1, -1))
    val.get_or_create_version((2, -1, -1))

    # check that index is working
    assert val.index(component.Version((3, -1, -1))) == 2

    # check that index is throwing exception
    with pytest.raises(ValueError):
        val.index(component.Version((6, -1, -1)))

    # check that index is throwing exception when searching for version
    with pytest.raises(ValueError):
        val.get('6')

    # basic access by index is working
    assert val[1] == component.Version((2, -1, -1))

    # basic access by negative index is working, as well as comparison against
    # version
    assert val[-1] == component.Version((4, -1, -1))

    # assert that slicing is working
    assert len(val[2:4]) == 2

    # assert that we can check if object is on the list
    assert component.Version((4, -1, -1)) in val

    # assert that list is sorted
    assert val[0] == component.Version((1, -1, -1))

    # assert we can check how many versions we have
    assert len(val) == 4

    # assert we can iterate over VersionList
    for idx, version in enumerate(val, 1):
        assert version == component.Version(idx)


def test_namespacing_works():
    version = component.Version('1.0.0')

    # first assert that we can add namespace and it's properly check if exists
    version.add('user')
    assert version.has('user') is True
    assert version.has('radio') is False
    assert version.has('car') is False

    version.add('radio')
    assert version.has('user') is True
    assert version.has('radio') is True
    assert version.has('car') is False

    version.add('car')
    assert version.has('user') is True
    assert version.has('radio') is True
    assert version.has('car') is True

    # assert number of namespaces is three
    assert len(version) == 3

    list_of_names = [
        'user',
        'radio',
        'car',
    ]

    # assert we can iterate over version
    for idx, namespace in enumerate(version):
        assert namespace.name == list_of_names[idx]

    # assert we cannot add second namespace with same name
    with pytest.raises(exception.RoutingConfigurationError):
        version.add('car')

    # assert we can get namespace with given name
    namespace = version.get('car')
    assert namespace.name == 'car'

    # assert we will get exception if namespace not found
    with pytest.raises(exception.RoutingConfigurationError):
        version.get('crocodile')
