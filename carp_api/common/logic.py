import collections

from flask import current_app


def get_pong(version=None):
    return 'pong - {}'.format(version) if version else 'pong'


def get_url_map(version=None):
    all_endpoints = []

    prefix = f'/{version}' if version else ''

    for rule in current_app.url_map.iter_rules():
        if rule.endpoint == 'static':
            continue

        if not rule.rule.startswith(prefix):
            continue

        endpoint = current_app.view_functions[rule.endpoint]

        methods = endpoint.methods \
            if endpoint.methods else ["GET", "HEAD", "OPTIONS"]

        all_endpoints.append((
            rule.rule,
            "({})".format(",".join(methods)),
            endpoint.get_short_documentation()
        ))

    all_endpoints.sort()

    result = collections.OrderedDict()

    for rule, methods, doc in all_endpoints:
        result[f"{rule} {methods}"] = doc

    return result
