import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid',
    'SQLAlchemy',
    'transaction',
    'pyramid_tm',
    'pyramid_debugtoolbar',
    'zope.sqlalchemy',
    'waitress',
    'alembic',
    'psycopg2',
    'webtest',
    'pyramid_jinja2',
    'pyramid_exclog',
    'alembic',
    'fabric',
    'passlib',
    'Babel',
    'lingua',
    'deform',
    'Dashboard',
    'requests-oauthlib',
    'mock',
    'Sphinx'
]

setup(name='WBComposting',
      version='0.1.0',
      description='WBComposting',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='composting',
      install_requires=requires,
      message_extractors={
          'composting': [
              ('**.py', 'lingua_python', None),
              ('**.jinja2', 'jinja2', None)]
      },
      entry_points="""\
      [paste.app_factory]
      main = composting:main
      [console_scripts]
      initialize_WBComposting_db = composting.scripts.initializedb:main
      createuser = composting.scripts.createuser:main
      """,
      )
