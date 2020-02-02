from carp_api.routing import router

from . import endpoints


router.enable('1.0', 'car', endpoints=[
    endpoints.GetListOfCars,
])
router.enable('1.0', 'tree', endpoints=[
    endpoints.GetListOfTrees,
])
