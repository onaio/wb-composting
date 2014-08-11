import datetime
import json
import os
import sys
import transaction

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,)

from ..models.base import (
    DBSession,
    Base,)

from dashboard.libs.submission_handler import (
    submission_handler_manager)
from composting.models import (
    Municipality,
    Skip)
from composting.models.site_report import SiteReport
from composting import hook_submission_handlers
from composting.models.user import User
from composting.tests.test_base import TestBase
from composting.security import pwd_context


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)

    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)

    Base.metadata.create_all(engine)

    setup_logging(config_uri)

    pwd_context.load_path(config_uri)

    # create models here
    admin = User(username='admin', password='admin', active=True,
                 group='nema')
    municipality = Municipality(name="Mukono")
    manager = User(username='manager', password='manager',
                   active=True, group='sm', municipality=municipality)
    skip_a = Skip(municipality=municipality, skip_type='A', small_length=20,
                  large_length=30, small_breadth=10, large_breadth=16)

    # add dummy site reports
    site_report_1 = SiteReport(
        report_date=datetime.date.today(),
        municipality=municipality,
        report_json={
            'volume_of_msw_processed': 400,
            'density_of_msw': 0.5,
            'quantity_of_msw_processed': 550,
            'num_trucks_delivered_msw': 20,
            'volume_of_mature_compost': 500,
            'density_of_mature_compost': 3.5,
            'conversion_factor_mature_to_sieved': 0.145,
            'quantity_of_compost_produced': 351,
            'quantity_of_compost_sold': 405,
            'vehicle_count': 15,
            'average_distance': 20,
            'volume_of_rejects_from_sieving': 500,
            'density_of_rejects_from_sieving': 450,
            'quantity_of_rejects_from_sieving_landfilled': 2.4,
            'total_windrow_samples': 14,
            'low_windrow_sample_count': 5,
            'fuel_consumption': 40,
            'electricity_consumption': 150,
            'leachete_volume_accumulated': 200})

    site_report_2 = SiteReport(
        report_date=datetime.date.today(),
        municipality=municipality,
        report_json={
            'volume_of_msw_processed': 300,
            'density_of_msw': 0.7,
            'quantity_of_msw_processed': 500,
            'num_trucks_delivered_msw': 15,
            'volume_of_mature_compost': 470,
            'density_of_mature_compost': 2.5,
            'conversion_factor_mature_to_sieved': 0.13,
            'quantity_of_compost_produced': 300,
            'quantity_of_compost_sold': 285,
            'vehicle_count': 12,
            'average_distance': 17,
            'volume_of_rejects_from_sieving': 130,
            'density_of_rejects_from_sieving': 150,
            'quantity_of_rejects_from_sieving_landfilled': 1.4,
            'total_windrow_samples': 14,
            'low_windrow_sample_count': 3,
            'fuel_consumption': 28,
            'electricity_consumption': 140,
            'leachete_volume_accumulated': 170})

    site_report_3 = SiteReport(
        report_date=datetime.date.today(),
        municipality=municipality,
        report_json={
            'volume_of_msw_processed': 200,
            'density_of_msw': 3,
            'quantity_of_msw_processed': 250,
            'num_trucks_delivered_msw': 10,
            'volume_of_mature_compost': 300,
            'density_of_mature_compost': 1.5,
            'conversion_factor_mature_to_sieved': 0.125,
            'quantity_of_compost_produced': 251,
            'quantity_of_compost_sold': 200,
            'vehicle_count': 9,
            'average_distance': 17,
            'volume_of_rejects_from_sieving': 300,
            'density_of_rejects_from_sieving': 175,
            'quantity_of_rejects_from_sieving_landfilled': 2,
            'total_windrow_samples': 10,
            'low_windrow_sample_count': 3,
            'fuel_consumption': 18,
            'electricity_consumption': 110,
            'leachete_volume_accumulated': 140})

    submission_handler_manager.clear()
    hook_submission_handlers()

    with transaction.manager:
        admin.save()
        municipality.save()
        manager.save()
        skip_a.save()
        site_report_1.save()
        site_report_2.save()
        site_report_3.save()

        for status, raw_json in TestBase.submissions:
            json_payload = json.loads(raw_json)
            handler_class = submission_handler_manager.find_handler(
                json_payload)
            handler_class().__call__(json_payload, status=status)
