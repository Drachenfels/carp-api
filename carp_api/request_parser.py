import re

from carp_api import exception


def form_to_python(payload):
    """Function converts any form-encoded payload (as served by flask's
    request.values) to dictionary using set of rules.

    Rules:
        - if given value appears once, it's assumed it's a value:
            ie. name=john will end up as 'name': 'john'
        - if given value appears several times, it's assumed it's a list
            ie. name=john&name=gwen will end up as 'name': ['john', 'gwen']
        - if given value appears to be legacy array format, it's assumed it's a
          list:
            ie. name[]=john will end up as name: ['john']
        - if given value appears in custom array format, it's assumed it's a
          list in that order:
            ie. name[0]=john&name[1]=emma will end up as ['john', 'emma']
        - if given key has dots in name, it will appear as an object:
            ie. user.name=john&user.age=23 will end up as
                {'name': 'john', 'age': 23'}
        - if given key has dots and is using custom array format it will be
          list of objects:
            ie. user[0].name=john&user[0].age=23& \
                user[1].name=emma&user[1].age=30
                will end up as [
                    {'name': 'john', 'age': 23},
                    {'name': 'emma', 'age': 30},
                ]
        - if given key is a dot (so object) but is using legacy format, only
        one attribute can be passed or multiple different attributes of one
        object.
            ie. user[].name=john&user[].name=emma will end up as:
                [{'name': 'john'}, {'name': 'emma'}]

            or
                user[].name=john&user[].age=23 will end up as:
                ['name': 'john', 'age': 23}

            but will cause exception in any other case
    """
    flat_tree = _flatten_payload(payload)

    baobab = {}

    for structure, value in flat_tree:
        _build_tree(baobab, structure, value)

    # while building lists, we use custom class Array, we need to convert them
    # back to standard python primitve
    baobab = _array_to_list(baobab)

    return baobab


def _array_to_list(some_value):
    if isinstance(some_value, Array):
        return [
            _array_to_list(sub_elm) for sub_elm in some_value.to_list()
        ]

    if isinstance(some_value, dict):
        for key, value in some_value.items():
            some_value[key] = _array_to_list(value)

    return some_value


def _build_tree(construct, structure, value):
    # ie. we have:
    # ('user', 0, 'address', 2) => 'e16'
    # ('user', 0, 'address', 1) => 'w1'

    # ('name',) => 'zbig'

    # ('user', 'name') => 'zbig'
    # ('user', 'age') => '10'

    if len(structure) == 1:
        if structure[0] == -1:
            if isinstance(value, list):
                for sub_val in value:
                    construct.append(sub_val)
            else:
                construct.append(value)
        else:
            construct[structure[0]] = value

    else:
        if structure[0] not in construct:
            next_construct = Array() if isinstance(structure[1], int) else {}
        else:
            next_construct = construct[structure[0]]

        construct[structure[0]] = _build_tree(
            next_construct, structure[1:], value)

    return construct


class Array:
    def __init__(self):
        self.container = {}

    def __setitem__(self, key, value):
        if not isinstance(key, int):
            raise ValueError("Only number can be used as an index of Array")

        self.container[key] = value

    def __getitem__(self, key):
        return self.container[key]

    def __contains__(self, key):
        return key in self.container

    def __len__(self):
        return len(list(self.container.keys()))

    def get_last_key(self):
        keys = list(self.container.keys())
        keys.sort()

        return keys[-1] if keys else None

    def to_list(self):
        keys = list(self.container.keys())
        keys.sort()

        result = [self.container[key] for key in keys]

        return result

    def append(self, value):
        last_key = self.get_last_key()

        key = 0 if last_key is None else last_key + 1

        self[key] = value


def _flatten_payload(payload):
    flat_tree = []

    for key, value in payload.lists():
        line = []

        if '.' in key and '[]' in key and not key.endswith('[]'):
            raise exception.InvalidPayloadError(
                'It is impossible to mix append with objects, '
                'please use explicit index. '
                'Instead of user[].name do user[1].name')

        if '.' in key:
            bits = key.split('.')

            for bit in bits:
                if bit[-1] == '':
                    raise exception.InvalidPayloadError(
                        'Dot . is used to distinguish between object '
                        'and simple key, and has to be followed by '
                        'non-empty string. For example user.name means '
                        'object user with attribute name')

                line += _add_key(bit)
        else:
            line += _add_key(key)

        if line[-1] == 1:
            for current_val in value:
                flat_tree.append(
                    (tuple(line), current_val))
        else:
            flat_tree.append(
                (tuple(line), value[0] if len(value) == 1 else value))

    # at this point all lists should be converted into flat list, if we sort
    # them end effect will be safe to build a tree from

    try:
        flat_tree.sort()
    except TypeError:
        raise exception.InvalidPayloadError(
            'Unable to parse payload, looks like object is a mix of an array '
            'and attributes. Ie. user.name=Dan&user[0].name=Stef')

    return flat_tree


def _add_key(key):
    line = []
    pattern = r'(\w+)\[(\d)*\]'

    match = re.match(pattern, key)

    key, idx = match.groups() if match else (key, 'NoMatch')

    line.append(key)

    if idx != 'NoMatch':
        line.append(-1 if idx is None else int(idx))

    return line
