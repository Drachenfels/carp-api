from flask import current_app, request
from simple_settings import settings


def generate_session_key(uid):
    """Generate unique session_key per user, per api instance.

    NOTE: session_namespace is api instance, if you have just one api leave it
    as is. Otherwise override it in settings.
    """
    return '{session_namespace}_auth_token_{uid}'.format(
        session_namespace=settings.SESSION_NAMESPACE, uid=uid)


def make_error_code(attribute, schema):
    attr_code = settings.ERROR_CODEBOOK_ATTRIBUTES.get(attribute, None)
    schema_code = settings.ERROR_CODEBOOK_SCHEMA.get(schema, None)

    if attr_code is None or schema_code is None:
        current_app.logger.info(
            "Error code could not be generated. "
            "Attr code: %s or Schma code: %s, is None", attr_code, schema_code)

        attr_code = -1
        schema_code = -1

    return "{}::{}".format(attr_code, schema_code)


def cors_headers():
    headers = {}
    if 'Origin' not in request.headers:
        current_app.logger.info('CORS. No Origin header')
    else:
        origin = request.headers['Origin']
        current_app.logger.info('CORS. Origin header: %s', origin)

        valid_domains = settings.CORS_ALLOWED_HOSTS
        current_app.logger.info('Valid domains %s', valid_domains)

        for valid_domain in valid_domains:
            current_app.logger.info(
                'CORS. Origin %s in valid domains %s?',
                origin, valid_domains
            )
            if valid_domain in origin:
                headers['Access-Control-Allow-Origin'] = origin
                headers['Access-Control-Allow-Credentials'] = \
                    'true'
                headers['Access-Control-Allow-Headers'] = (
                    'Accept,'
                    'Accept-Language,'
                    'Authorization,'
                    'Content-Language,'
                    'Content-Type'
                )
                current_app.logger.info('CORS. Valid origin: %s', origin)
                break
        else:
            current_app.logger.info('CORS. Invalid origin: %s', origin)
    return headers


def build_tree(list_of_strings):
    """Function takes a list of strings, ie:

    user.address.city
    user.address.postcode
    user.name.first
    user.name.last
    user.age

    And builds a tree of nested dictionaries.
    """
    tree = {}
    node = tree

    for key in list_of_strings:
        if '.' in key:
            bits = key.split('.')

            for bit in bits[:-1]:
                if bit not in list(node.keys()) or node[bit] is None:
                    node[bit] = {}

                node = node[bit]

            node[bits[-1]] = None
        else:
            node[key] = None

        node = tree

    return tree
