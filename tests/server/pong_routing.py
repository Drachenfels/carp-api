from carp_api.routing import router

from . import endpoints  # NOQA


# to use pong we need to disable common routes as they are using conflicting
# urls
router.enable(endpoints=[
    endpoints.UberPong,
])
