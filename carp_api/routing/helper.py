from carp_api import exception


def normalise_version(version, length=3):
    """Normalise whatever comes into standard tuple of integers (default: 3)
    """
    if version is None:
        version = []

    if isinstance(version, (int, float)):
        version = str(version)

    if isinstance(version, str):
        version = version.split('.')

    version = list(version)

    # at this stage we should have a list or tuple of values

    normalised_version = []

    while version:
        try:
            value = version.pop(0)

            value = int(value) if value != '' else -1

        except (TypeError, ValueError):
            raise exception.RoutingConfigurationError(
                "Version number is not an integer, got {}".format(version)
            )

        if value < -1:
            raise exception.RoutingConfigurationError(
                "Version number needs to be equal or greater than -1, "
                "got {}".format(value)
            )

        if value > -1 and normalised_version and normalised_version[-1] == -1:
            raise exception.RoutingConfigurationError(
                "Preceding version number is -1, cannot add lesser version "
                "after that, got {}".format(value)
            )

        normalised_version.append(value)

    while len(normalised_version) < length:
        normalised_version.append(-1)

    return tuple(normalised_version)


def get_endpoint_name(obj):
    default_name = (
        obj.__name__ if isinstance(obj, type) else
        obj.__class__.__name__
    )

    return getattr(obj, 'name', default_name)
