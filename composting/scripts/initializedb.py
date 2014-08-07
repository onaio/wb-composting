import os
import sys
import transaction
import json

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

    submission_handler_manager.clear()
    hook_submission_handlers()

    with transaction.manager:
        admin.save()
        municipality.save()
        manager.save()
        skip_a.save()

        for status, raw_json in TestBase.submissions:
            json_payload = json.loads(raw_json)
            handler_class = submission_handler_manager.find_handler(
                json_payload)
            handler_class().__call__(json_payload, status=status)
