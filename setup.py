import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
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
    'Dashboard'
]

setup(name='WBComposting',
      version='0.0',
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
      test_suite='wbcomposting',
      install_requires=requires,
      message_extractors={
          'wbcomposting': [
              ('**.py', 'lingua_python', None),
              ('**.jinja2', 'jinja2', None)]
      },
      entry_points="""\
      [paste.app_factory]
      main = wbcomposting:main
      [console_scripts]
      initialize_WBComposting_db = wbcomposting.scripts.initializedb:main
      """,
      )
