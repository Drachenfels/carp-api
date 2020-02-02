from carp_api.routing import component


class Router:
    versions = component.VersionList()

    @classmethod
    def enable(cls, version=None, namespace=None, endpoints=None):
        if namespace is None:
            namespace = ''

        version = cls.versions.get_or_create_version(version)

        if not version.has(namespace):
            version.add(namespace)

        namespace = version.get(namespace)

        namespace.add(endpoints)

    @classmethod
    def get_final_routing(cls):
        """Classmethod returns final routing, it means that all endpoints that
        should propagate do so, overrides are applied and any potential
        conflict is flagged by exception.

        Main premise is that whenever new version is being enabled, we
        propagate all the endpoints from previous versions to the new one. At
        will we can override old enpoint with new implementation. It's default
        behaviour of endpoint that we can turn off per endpoint basis. If
        version is set to None it means that endpoint is not versioned at all
        and won't use any version prefix on url.
        """
        final_routing = component.VersionList()

        for version in cls.versions:
            previous_version = (
                final_routing[-1] if final_routing else component.Version()
            )

            current_version = final_routing.get_or_create_version(version)

            # namespaces existing both in old and new version
            common_namespaces = previous_version & version

            # namespaces existing only in old version
            propagating_namespaces = previous_version - version

            # namespaces existing only in new version
            new_namespaces = version - previous_version

            for name in common_namespaces:
                current_version.add(name)

                old_endpoints = previous_version.get(name).endpoints
                new_endpoints = version.get(name).endpoints

                current_version.get(name).add(list(new_endpoints.values()))

                old_endpoints = [
                    endpoint for name, endpoint in old_endpoints.items()
                    if name not in new_endpoints and endpoint.propagate is True
                ]

                current_version.get(name).add(old_endpoints)

            for name in propagating_namespaces:
                current_version.add(name)

                current_version.get(name).add([
                    endpoint for endpoint in previous_version.get(
                        name).endpoints.values()
                    if endpoint.propagate is True
                ])

            for name in new_namespaces:
                current_version.add(name)

                current_version.get(name).add(
                    version.get(name).endpoints.values()
                )

        return final_routing


def enable(version=None, namespace=None, endpoints=None):
    """Wrapping function for convenience.
    """
    Router.enable(version, namespace, endpoints)
