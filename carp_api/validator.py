import datetime
import functools

# pylint: disable=unused-import
from validators import (  # NOQA
    between, domain, email, iban, ipv4, ipv6, length, mac_address, slug,
    truthy, url, uuid, ValidationFailure)
# pylint: enable=unused-import

from carp_api import exception

from . import datetime_helper


def validate_is_not_none(*args, **kwargs):
    """Retry calling the decorated function:
    :param times: number of times to try before giving up
    :param delay: delay between retries in seconds
    """
    def decorator(func):
        @functools.wraps(func)
        def func_wrapper(*args, **kwargs):
            if args[1] is None:
                return truthy(False)

            return func(*args, **kwargs)

        return func_wrapper
    return decorator


class BaseValidator:
    validated_value = None

    def __init__(self, message=None):
        self.message = message

    def __call__(self, value):
        resp = self.validate(value)

        self.validated_value = value

        message = self.message if self.message else self.default_message

        if not resp:
            raise exception.ValidationError(message)

    @property
    def default_message(self):
        return "Validation error"

    def validate(self, value):
        return NotImplementedError(
            "Implement method validate that will return either True or False")


class IsMinLength(BaseValidator):
    def __init__(self, min_, *args, **kwargs):
        self.min = min_

        super().__init__(*args, **kwargs)

    @validate_is_not_none()
    def validate(self, value):
        return length(value, min=self.min)

    @property
    def default_message(self):
        return "String needs ot be of minimal length {}".format(self.min)


class IsEmail(BaseValidator):
    @validate_is_not_none()
    def validate(self, value):
        return email(value)

    @property
    def default_message(self):
        return "Value is not a valid email: {}".format(self.validated_value)


class IsPostcode(BaseValidator):
    @validate_is_not_none()
    def validate(self, value):
        return length(value, min=1, max=8)

    @property
    def default_message(self):
        return "Value is not a valid postcode: {}".format(self.validated_value)


class IsInFuture(BaseValidator):
    @validate_is_not_none()
    def validate(self, value):
        """Validator works under assumption that value is valid datetime
        object.
        """
        now = datetime_helper.get_current_server_time()

        if isinstance(value, datetime.date):
            now = now.date()

        return truthy(value > now)

    @property
    def default_message(self):
        return "Date object is not in the future: {}".format(
            self.validated_value)


class IsPositiveInteger(BaseValidator):
    @validate_is_not_none()
    def validate(self, value):
        return truthy(value >= 0)

    @property
    def default_message(self):
        return "Value is not a positive number"


class IsAtLeastOne(BaseValidator):
    @validate_is_not_none()
    def validate(self, value):
        return truthy(len(value) >= 1)

    @property
    def default_message(self):
        return "At least one value needs to be present on the list"


class IsUid(IsPositiveInteger):
    @property
    def default_message(self):
        return "Value is not a valid uid (integer number bigger than 0)"


class IsNonEmpty(BaseValidator):
    @validate_is_not_none()
    def validate(self, value):
        return length(value, min=1)

    @property
    def default_message(self):
        return "Value cannot be empty"
