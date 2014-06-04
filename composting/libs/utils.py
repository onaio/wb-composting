import pytz
import datetime
from datetime import timedelta

from pyramid.i18n import TranslationStringFactory


translation_string_factory = TranslationStringFactory('WBComposting')


def get_month_start_end(date):
    """
    Get the start and end days for date's month
    """
    # using 31 will ALWAYS roll us over to the next month and possibly year
    date_next_month = date + timedelta(31)
    return (datetime.date(date.year, date.month, 1),
            datetime.date(date_next_month.year, date_next_month.month, 1)
            - timedelta(1))


def get_locale_time_from_utc_time(utc_date_time, tzname='Africa/Kampala'):
    timezone = pytz.timezone(tzname)
    utc_time = pytz.utc.localize(utc_date_time)
    return utc_time.astimezone(timezone)