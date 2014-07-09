import logging.config

from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from sqlalchemy import engine_from_config

from dashboard.libs.submission_handler import submission_handler_manager

from composting.security import group_finder, pwd_context, friendly_group_name
from composting.libs.municipality_submission_handler import (
    MunicipalitySubmissionHandler)
from composting.libs.windrow_monitoring_handler import (
    WindrowMonitoringHandler)
from composting.models.base import (
    DBSession,
    Base,
)
from composting.models.municipality import MunicipalityFactory
from composting.models.user import UserFactory
from composting.models.submission import SubmissionFactory
from composting.models.skip import SkipFactory
from composting.models.windrow_monitoring import WindrowMonitoringFactory
from composting.views.helpers import is_current_path, get_request_user


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    session_factory = UnencryptedCookieSessionFactoryConfig(
        settings['secret_key'])
    config = Configurator(settings=settings,
                          root_factory='composting.models.base.RootFactory',
                          session_factory=session_factory)
    config.set_authentication_policy(
        AuthTktAuthenticationPolicy(settings['secret_key'],
                                    callback=group_finder,
                                    hashalg='sha512'))

    config.set_authorization_policy(ACLAuthorizationPolicy())
    config.set_default_permission('authenticated')

    logging.config.fileConfig(
        global_config['__file__'], disable_existing_loggers=False)

    # configure password context
    pwd_context.load_path(global_config['__file__'])

    # include ourselves
    includeme(config)
    return config.make_wsgi_app()


def hook_submission_handlers():
    submission_handler_manager.add_handler(MunicipalitySubmissionHandler)
    submission_handler_manager.add_handler(WindrowMonitoringHandler)


def includeme(config):
    config.include('dashboard')
    config.commit()

    config.get_jinja2_environment().filters['friendly_group_name'] =\
        friendly_group_name

    # hook up our submission handlers
    hook_submission_handlers()

    # request methods
    config.add_request_method(get_request_user, 'user', reify=True)
    config.add_request_method(is_current_path)

    # pyramid_jinja2 is already included by Dashboard
    config.add_jinja2_search_path("composting:templates")

    config.add_static_view('static', 'composting:static', cache_max_age=3600)
    config.add_static_view('docs', '../docs/_build/html', cache_max_age=3600)
    config.add_route('default', '/')
    config.add_route('auth', '/auth/{action}')
    config.add_route('oauth', '/oauth/{action}')
    config.add_route('municipalities', '/municipalities/*traverse',
                     factory=MunicipalityFactory)
    config.add_route('submissions', '/submissions/*traverse',
                     factory=SubmissionFactory)
    config.add_route('skips', '/skips/*traverse',
                     factory=SkipFactory)
    config.add_route('users', '/users/*traverse',
                     factory=UserFactory)
    config.scan()
