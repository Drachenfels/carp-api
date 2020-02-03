import json
import os
import subprocess

from urllib import request

import pytest


def _make_server(env=None):
    proc = subprocess.Popen(
        ['python', '-m', 'carp_api', 'run'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
        env=env, text=True
    )

    try:
        proc.wait(timeout=0.5)

        if proc.returncode > 0:
            lines = [
                line.strip('\n') for line in proc.stderr.readlines()
                if line.strip('\n')
            ]

            raise ValueError(lines[-1])
    except subprocess.TimeoutExpired:
        # only dead process will respond to communicate, otherwise server is
        # waiting for connection thus timeout on communicate
        pass

    return proc


def _make_request(url, is_json=False):
    with request.urlopen('http://localhost:5000/' + url) as response:
        content = response.read().decode('utf8').strip('"\n')

    if is_json:
        content = json.loads(content)

    return content


@pytest.fixture
def default_server():
    proc = _make_server()

    yield

    proc.kill()


@pytest.fixture
def rich_server():
    old_settings = os.environ['SIMPLE_SETTINGS']

    os.environ['SIMPLE_SETTINGS'] = 'tests.server.settings.base'

    proc = _make_server(os.environ)

    yield

    os.environ['SIMPLE_SETTINGS'] = old_settings

    proc.kill()


@pytest.fixture
def conflicted_server():
    old_settings = os.environ['SIMPLE_SETTINGS']

    os.environ['SIMPLE_SETTINGS'] = 'tests.server.settings.conflicted_base'

    yield

    os.environ['SIMPLE_SETTINGS'] = old_settings


@pytest.fixture
def override_pong():
    old_settings = os.environ['SIMPLE_SETTINGS']

    os.environ['SIMPLE_SETTINGS'] = 'tests.server.settings.pong_base'

    yield

    os.environ['SIMPLE_SETTINGS'] = old_settings


@pytest.mark.end_to_end
def test_app_is_working(default_server):
    """Simply check if we can build a server and send ping request using
    default settings.
    """
    response = _make_request('ping/')

    assert response == 'pong'


@pytest.mark.end_to_end
def test_rich_app_is_working(rich_server):
    """This server uses additional routing configuration, we are going to test
    if it's still ok in such case.
    """
    response = _make_request('ping/')

    assert response == 'pong'

    response = _make_request('1.0/car/', is_json=True)

    assert len(response) == 3
    assert 'HappyCar' in response
    assert 'SadCar' in response
    assert 'YoloCar' in response

    response = _make_request('1.0/tree/', is_json=True)

    assert len(response) == 3
    assert 'BigTree' in response
    assert 'SmallTree' in response
    assert 'Shrub' in response


@pytest.mark.end_to_end
def test_conflicting_urls_are_not_working(conflicted_server):
    """Server is fine but two endpoints are sharing same url.
    """
    with pytest.raises(ValueError, match=r'.*ConflictingUrlsError.*'):
        _make_server(os.environ)


@pytest.mark.end_to_end
def test_uber_pong_app_is_working(override_pong):
    """Default server with new implementation of pong endpoint.
    """
    response = _make_request('ping/')

    assert response == 'uber-pong'
