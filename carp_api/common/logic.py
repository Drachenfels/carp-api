import collections

from flask import current_app


def get_pong(version=None):
    return 'pong - {}'.format(version) if version else 'pong'


def get_url_map(version=None):
    func_list = collections.OrderedDict()

    prefix = '/{}'.format(version) if version else ''

    for rule in current_app.url_map.iter_rules():
        if rule.endpoint == 'static':
            continue

        if not rule.rule.startswith(prefix):
            continue

        endpoint = current_app.view_functions[rule.endpoint]

        methods = endpoint.methods \
            if endpoint.methods else ["GET", "HEAD", "OPTIONS"]

        key = "({}) {}".format(",".join(methods), rule.rule)

        func_list[key] = endpoint.short_documentation

    return func_list
