import logging.config

from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from sqlalchemy import engine_from_config

from dashboard.libs.submission_handler import submission_handler_manager

from composting.security import group_finder, pwd_context
from composting.libs.daily_waste_register_handler import (
    DailyWasteSubmissionHandler)
from composting.libs.monthly_density_handler import (
    MonthlyDensityHandler)
from composting.models.base import (
    DBSession,
    Base,
)
from composting.models.municipality import MunicipalityFactory
from composting.models.daily_waste import DailyWasteFactory
from composting.models.skip import SkipFactory


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

    logging.config.fileConfig(
        global_config['__file__'], disable_existing_loggers=False)

    # configure password context
    pwd_context.load_path(global_config['__file__'])

    # include ourselves
    includeme(config)
    return config.make_wsgi_app()


def hook_submission_handlers():
    submission_handler_manager.add_handler(MonthlyDensityHandler)
    submission_handler_manager.add_handler(DailyWasteSubmissionHandler)


def includeme(config):
    config.include('dashboard')
    config.commit()

    # hook up our submission handlers
    hook_submission_handlers()

    # pyramid_jinja2 is already included by Dashboard
    config.add_jinja2_search_path("composting:templates")

    config.add_static_view('static', 'composting:static', cache_max_age=3600)
    config.add_route('default', '/')
    config.add_route('municipalities', '/municipalities/*traverse',
                     factory=MunicipalityFactory)
    config.add_route('daily-waste', '/daily-waste/*traverse',
                     factory=DailyWasteFactory)
    config.add_route('skips', '/skips/*traverse',
                     factory=SkipFactory)
    config.scan()
