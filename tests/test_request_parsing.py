"""Framework employs additional and non-standard request parsing, this test
suit checks if everything is working as intended.
"""

import pytest

from werkzeug.datastructures import CombinedMultiDict, MultiDict

from carp_api import request_parser, exception


def test_parsing_request_simple_case():
    post = MultiDict([
        ('name', 'john')
    ])
    get = MultiDict([
    ])

    payload = CombinedMultiDict([get, post])

    result = request_parser.form_to_python(payload)

    assert result['name'] == 'john'

    post = MultiDict([
        ('name', 'john')
    ])
    get = MultiDict([
        ('name', 'emma')
    ])

    payload = CombinedMultiDict([get, post])

    result = request_parser.form_to_python(payload)

    assert result['name'][0] in ['john', 'emma']
    assert result['name'][1] in ['john', 'emma']


def test_parsing_request_key_several_times():
    post = MultiDict([
        ('name', 'john2'),
        ('name', 'john1'),
    ])
    get = MultiDict([
    ])

    payload = CombinedMultiDict([get, post])

    result = request_parser.form_to_python(payload)

    assert result['name'][0] in ['john1', 'john2']
    assert result['name'][1] in ['john1', 'john2']

    post = MultiDict([
        ('name', 'john2'),
        ('name', 'john1'),
    ])
    get = MultiDict([
        ('name', 'john3')
    ])

    payload = CombinedMultiDict([get, post])

    result = request_parser.form_to_python(payload)

    assert result['name'][0] in ['john1', 'john2', 'john3']
    assert result['name'][1] in ['john1', 'john2', 'john3']
    assert result['name'][2] in ['john1', 'john2', 'john3']


def test_parsing_request_key_in_legacy_format():
    post = MultiDict([
    ])
    get = MultiDict([
        ('name[]', 'john1'),
        ('name[]', 'john2'),
    ])

    payload = CombinedMultiDict([get, post])

    result = request_parser.form_to_python(payload)

    assert result['name'][0] in ['john1', 'john2']
    assert result['name'][1] in ['john1', 'john2']

    post = MultiDict([
    ])
    get = MultiDict([
        ('name[]', 'john2'),
    ])

    payload = CombinedMultiDict([get, post])

    result = request_parser.form_to_python(payload)

    assert result['name'] == ['john2']


def test_parsing_request_keys_are_ordered():
    post = MultiDict([
        ('name[3]', 'john3'),
        ('name[2]', 'john2'),
    ])
    get = MultiDict([
        ('name[1]', 'john1'),
        ('name[0]', 'john0'),
    ])

    payload = CombinedMultiDict([get, post])

    result = request_parser.form_to_python(payload)

    assert result['name'][0] == 'john0'
    assert result['name'][1] == 'john1'
    assert result['name'][2] == 'john2'
    assert result['name'][3] == 'john3'


def test_parsing_request_keys_an_object():
    post = MultiDict([
        ('user.name', 'john'),
        ('user.age', '23'),
    ])
    get = MultiDict([
    ])

    payload = CombinedMultiDict([get, post])

    result = request_parser.form_to_python(payload)

    assert result['user']['name'] == 'john'
    assert result['user']['age'] == '23'

    post = MultiDict([
    ])
    get = MultiDict([
        ('user.name', 'john'),
        ('user.age', '23'),
    ])

    payload = CombinedMultiDict([get, post])

    result = request_parser.form_to_python(payload)

    assert result['user']['name'] == 'john'
    assert result['user']['age'] == '23'


def test_object_has_multiple_values_on_attr():
    post = MultiDict([
        ('user.name[0]', 'john'),
        ('user.age[1]', '23'),
        ('user.name[1]', 'emma'),
        ('user.age[0]', '30'),
    ])
    get = MultiDict([
    ])

    payload = CombinedMultiDict([get, post])

    result = request_parser.form_to_python(payload)

    assert result['user']['name'][0] == 'john'
    assert result['user']['name'][1] == 'emma'

    assert result['user']['age'][0] == '30'
    assert result['user']['age'][1] == '23'


def test_objects_are_lists():
    post = MultiDict([
        ('user[0].name', 'stefan'),
        ('user[2].name', 'ben'),
        ('user[1].name', 'josh'),
        ('user[0].age', '20'),
        ('user[2].age', '40'),
        ('message', 'hi'),
        ('user[1].age', '30'),
    ])
    get = MultiDict([
    ])

    payload = CombinedMultiDict([get, post])

    result = request_parser.form_to_python(payload)

    assert result['user'][0]['name'] == 'stefan'
    assert result['user'][0]['age'] == '20'

    assert result['user'][1]['name'] == 'josh'
    assert result['user'][1]['age'] == '30'

    assert result['user'][2]['name'] == 'ben'
    assert result['user'][2]['age'] == '40'


def test_various_edge_cases_success():
    post = MultiDict([
        ('user.name[]', 'john'),
        ('user.age[]', '30'),
    ])
    get = MultiDict([
    ])

    payload = CombinedMultiDict([get, post])

    result = request_parser.form_to_python(payload)

    assert result['user']['name'] == ['john']
    assert result['user']['age'] == ['30']

    post = MultiDict([
        ('user.name[]', 'john'),
        ('user.name[]', 'emma'),
    ])
    get = MultiDict([
    ])

    payload = CombinedMultiDict([get, post])

    result = request_parser.form_to_python(payload)

    assert result['user']['name'] == ['john', 'emma']


def test_various_edge_cases_unsuccessful():
    post = MultiDict([
        ('user[].name', 'sigsmund'),
        ('user[].age', '30'),
        ('user[].name', 'zygrfyd'),
    ])
    get = MultiDict([
    ])

    payload = CombinedMultiDict([get, post])

    with pytest.raises(exception.InvalidPayloadError):
        request_parser.form_to_python(payload)

    post = MultiDict([
        ('user[0].name', 'watson'),
        ('user.name', 'sherlock'),
    ])
    get = MultiDict([
    ])

    payload = CombinedMultiDict([get, post])

    with pytest.raises(exception.InvalidPayloadError):
        request_parser.form_to_python(payload)
