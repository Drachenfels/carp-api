import datetime
import re

import pytz

from simple_settings import settings
from dateutil import parser as date_parser

from carp_api import exception


def get_current_utc_time():
    """Creates fresh date object for a UTC timezone
    """
    date_obj = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    return date_obj


def get_current_server_time():
    """Creates fresh date object in whatever timezone is set for carp_api
    """
    date_obj = get_current_utc_time()

    return add_timezone(date_obj, settings.DEFAULT_TIMEZONE)


def add_timezone(date_obj, timezone):
    """Changes timezone to already non-naive dateobject (basically moves by
    offset as needed)
    """
    zone = pytz.timezone(timezone)

    date_obj = date_obj.astimezone(zone)

    return date_obj


def parse_into_datetime(value):
    '''Parse a string or datetime object into a datetime
    '''
    if not value:
        raise ValueError(
            "Object needs to be non-empty in order to parse it as a datetime")

    value = value.isoformat() if hasattr(value, 'isoformat') else str(value)

    date_obj = date_parser.parse(value)

    if date_obj.tzinfo is None:
        date_obj = add_timezone(
            date_obj.replace(tzinfo=pytz.utc), settings.DEFAULT_TIMEZONE)

    return date_obj


def parse_into_date(value):
    '''Parse a string or date object into a date object
    '''
    if not value:
        raise ValueError(
            "Object needs to be non-empty in order to parse it as a date")

    value = value.isoformat() if hasattr(value, 'isoformat') else str(value)

    date_obj = date_parser.parse(str(value))

    return datetime.date(*date_obj.timetuple()[:3])


def parse_into_time(value):
    '''Parse a string or timedelta into a timedelta object
    '''
    if not value:
        raise ValueError(
            "Object needs to be non-empty in order to parse it "
            "as a time object")

    pattern_with_colons = (
        r'^(?P<hours>\d{2})'
        r'(:(?P<minutes>\d{2}))'
        r'(:(?P<seconds>\d{2}))?'
        r'(:(?P<milliseconds>\d{2}))?$'
    )

    pattern_verbose = (
        r'((?=.*?(?P<minutes>\d+)\s*(m(\s|\d|:|$)+|minute(s)*)))?'
        r'((?=.*?(?P<milliseconds>\d+)\s*(ms(\s|\d|:|$)+|millisecond(s)*)))?'
        r'((?=.*?(?P<hours>\d+)\s*(h(\s|\d|:|$)+|hour(s)*)))?'
        r'((?=.*?(?P<seconds>\d+)\s*(s(\s|\d|:|$)+|second(s)*)))?'
    )

    for pattern in [pattern_with_colons, pattern_verbose]:
        regexp = re.search(pattern, value)

        if regexp:
            break

    if not regexp:
        raise exception.PayloadError(
            "Unable to recognise time value, got: {}".format(value))

    dct = {}

    if regexp.group('hours'):
        dct['hours'] = int(regexp.group('hours'))

    if regexp.group('minutes'):
        dct['minutes'] = int(regexp.group('minutes'))

    if regexp.group('seconds'):
        dct['seconds'] = int(regexp.group('seconds'))

    if regexp.group('milliseconds'):
        dct['milliseconds'] = int(regexp.group('milliseconds'))

    return datetime.timedelta(**dct)
