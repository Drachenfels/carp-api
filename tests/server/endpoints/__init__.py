from carp_api import endpoint


class GetListOfCars(endpoint.BaseEndpoint):
    url = ''

    def action(self):
        return [
            'HappyCar', 'SadCar', 'YoloCar',
        ]


class GetListOfTrees(endpoint.BaseEndpoint):
    url = ''

    def action(self):
        return [
            'BigTree', 'SmallTree', 'Shrub',
        ]


class GetListOfCarsWithCustomUrl(GetListOfCars):
    url = ''

    def action(self):
        return [
            'HappyCar', 'SadCar', 'YoloCar',
        ]

    def get_final_url(self, version, namespace):
        return '/yolo/'


class GetListOfTreesWithCustomUrl(GetListOfTrees):
    url = ''

    def action(self):
        return [
            'BigTree', 'SmallTree', 'Shrub',
        ]

    def get_final_url(self, version, namespace):
        return '/yolo/'
