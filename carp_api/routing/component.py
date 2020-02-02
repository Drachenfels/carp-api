from carp_api import exception

from . import helper


class Namespace:
    def __init__(self, name):
        self.name = name
        self._endpoints = {}

    def add(self, endpoints):
        for endpoint in endpoints:
            name = helper.get_endpoint_name(endpoint)

            if self.has(endpoint):
                raise exception.DuplicateEndpointError(
                    f"Second endpoint with {name} already registered for "
                    "namespace"
                )

            self._endpoints[name] = endpoint

    def has(self, endpoint):
        name = helper.get_endpoint_name(endpoint)

        return name in self._endpoints

    @property
    def endpoints(self):
        return self._endpoints

    def __iter__(self):
        for endpoint in self.as_list():
            yield endpoint

    def __len__(self):
        return len(self._endpoints)

    def as_list(self):
        return list(self.endpoints.values())


class Version:
    def __init__(self, version=None):
        # to make easier to use, we assume that version may be passed as either
        # any normalisable value or will be already a version
        self.value = version.value if isinstance(version, Version) else \
            helper.normalise_version(version)
        self._container = {}
        self._index = 0

    def __assert_same_type(self, other):
        if not isinstance(other, Version):
            raise TypeError(
                "Version can be compared only to other Version object")

    def __lt__(self, other):
        self.__assert_same_type(other)

        return self.value < other.value

    def __le__(self, other):
        self.__assert_same_type(other)

        return self.value <= other.value

    def __eq__(self, other):
        self.__assert_same_type(other)

        return self.value == other.value

    def __ne__(self, other):
        self.__assert_same_type(other)

        return self.value == other.value

    def __gt__(self, other):
        self.__assert_same_type(other)

        return self.value == other.value

    def __ge__(self, other):
        self.__assert_same_type(other)

        return self.value == other.value

    def __str__(self):
        return f"<Version value={self.value}>"

    def __repr__(self):
        return f"Version({self.value})"

    def __len__(self):
        return len(self._container)

    def __iter__(self):
        self._index = 0

        return self

    def __next__(self):
        self._index += 1

        if self._index > len(self):
            raise StopIteration

        return list(self._container.values())[self._index - 1]

    def as_str(self):
        return '.'.join([
            str(elm) for elm in self.value if elm != -1
        ])

    def has(self, name):
        return name in self._container

    def add(self, name):
        if self.has(name):
            raise exception.RoutingConfigurationError(
                "Namespace already present on version"
            )

        self._container[name] = Namespace(name)

    def get(self, name):
        if not self.has(name):
            raise exception.RoutingConfigurationError(
                "Namespace not present on version"
            )

        return self._container[name]

    def __and__(self, other):
        self.__assert_same_type(other)

        return set(self._container.keys()) & set(other._container.keys())

    def __xor__(self, other):
        self.__assert_same_type(other)

        return set(self._container.keys()) ^ set(other._container.keys())

    def __or__(self, other):
        self.__assert_same_type(other)

        return set(self._container.keys()) | set(other._container.keys())

    def __sub__(self, other):
        self.__assert_same_type(other)

        return set(self._container.keys()) - set(other._container.keys())


class VersionList:
    def __init__(self):
        self._versions = []
        self._index = 0

    def get_or_create_version(self, version):
        version = Version(version)

        if version not in self:
            self.append(version)

        return self.get(version)

    def append(self, version):
        self._versions.append(Version(version))
        self._versions.sort()

    def get(self, searched_version):
        searched_version = Version(searched_version)

        idx = self.index(searched_version)

        return self[idx]

    def index(self, searched_version):
        searched_version = Version(searched_version)

        for idx, version in enumerate(self):
            if searched_version == version:
                return idx

        raise ValueError(f'{searched_version} is not in list')

    def __iter__(self):
        self._index = 0

        return self

    def __next__(self):
        self._index += 1

        if self._index > len(self._versions):
            raise StopIteration

        return self._versions[self._index - 1]

    def __len__(self):
        return len(self._versions)

    def __contains__(self, other):
        return other in self._versions

    def __getitem__(self, idx):
        return self._versions[idx]

    def __str__(self):
        result = []

        for version in self:
            result.append(version.as_str())

            for namespace in version:
                result.append('{}-> {}'.format(' ' * 4, namespace.name))

                for endpoint in namespace:
                    endpoint_name = helper.get_endpoint_name(endpoint)

                    url = endpoint.get_final_url(
                        version=version.as_str(), namespace=namespace.name)

                    methods = '|'.join(endpoint.methods)

                    result.append('{}-> ({}) {} {}'.format(
                        ' ' * 8, methods, url, endpoint_name
                    ))

        return '\n'.join(result)

    def as_flat_list(self):
        """Flattens the structure into simple list of tuples of (version, name,
        specific endpoint).
        """
        result = []

        for version in self:
            for namespace in version:
                result.append((
                    version.as_str(), namespace.name, namespace.endpoints
                ))

        # sorting end result will help a bit to reassure stability
        result.sort()

        return result
