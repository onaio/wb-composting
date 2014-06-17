import os
import sys
import transaction

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from composting.security import pwd_context
from composting.models.base import DBSession
from composting.models.user import User


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> <username> <password> [nema|wb|env_officer|sm]\n'
          '(example: "%s development.ini john strongpassword")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 4:
        usage(argv)
    config_uri = argv[1]
    username = argv[2]
    password = argv[3]
    group = argv[4] if len(argv) > 4 else 'sm'
    if group not in ['nema', 'wb', 'env_officer', 'sm']:
        sys.stderr.write("Invalid group name: '{}'\n".format(group))
        sys.exit(1)
    setup_logging(config_uri)
    pwd_context.load_path(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    user = User(username=username, password=password, active=True, group=group)
    with transaction.manager:
        DBSession.add(user)
