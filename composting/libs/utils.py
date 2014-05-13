import re
import datetime

from pyramid.i18n import TranslationStringFactory


translation_string_factory = TranslationStringFactory('WBComposting')
TIMEZONE_RE = re.compile(r'\+.+$')


def remove_time_zone(date_string):
    return TIMEZONE_RE.sub('', date_string)


def date_string_to_date(date_string):
    # strip out the timezone i.e. +03[00]
    date_string = remove_time_zone(date_string)
    return datetime.datetime.strptime(
        date_string, '%Y-%m-%dT%H:%M:%S.%f').date()


def date_string_to_time(date_string):
    # strip out the timezone i.e. +03[00]
    date_string = remove_time_zone(date_string)
    return datetime.datetime.strptime(
        date_string, '%Y-%m-%dT%H:%M:%S.%f').time()