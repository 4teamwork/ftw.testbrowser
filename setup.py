import os
from setuptools import setup, find_packages


version = '1.5.2'


tests_require = [
    'Products.statusmessages',
    'ftw.builder',
    'plone.app.contenttypes',
    'plone.formwidget.autocomplete',
    'plone.z3cform',
    'unittest2',
    'z3c.form',
    'z3c.formwidget.query',
    'zope.configuration',
    'zope.publisher',
    'zope.schema',
    ]


setup(name='ftw.testbrowser',
      version=version,
      description='A test browser for Zope and Plone.',

      long_description=open('README.rst').read() + '\n' + \
          open(os.path.join('docs', 'HISTORY.txt')).read(),

      classifiers=[
        'Framework :: Plone',
        'Framework :: Plone :: 4.3',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],

      keywords='ftw browser testbrowser test',
      author='4teamwork GmbH',
      author_email='mailto:info@4teamwork.ch',
      url='https://github.com/4teamwork/ftw.testbrowser',

      license='GPL2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ftw', ],
      include_package_data=True,
      zip_safe=False,

      install_requires=[
        'lxml',
        'mechanize',
        'plone.app.testing',
        'plone.testing',
        'requests',
        'zope.component',
        'zope.interface',
        ],

      tests_require=tests_require,
      extras_require=dict(tests=tests_require),

      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
