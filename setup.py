import os
from setuptools import setup, find_packages


version = '2.1.3.dev0'


tests_require = [
    'Plone',
    'Products.CMFCore',
    'Products.CMFPlone',
    'Products.GenericSetup',
    'Products.statusmessages',
    'collective.z3cform.datagridfield',
    'ftw.builder >= 2.0.0.dev0',
    'ftw.testing >= 2.0.0.dev0',
    'plone.app.content',
    'plone.app.contenttypes',
    'plone.app.dexterity',
    'plone.app.testing',
    'plone.dexterity',
    'plone.i18n',
    'plone.z3cform',
    'transaction',
    'z3c.form',
    'z3c.formwidget.query',
    'z3c.relationfield',
    'zExceptions',
    'zope.configuration',
    'zope.globalrequest',
    'zope.publisher',
    'zope.schema',
    ]


extras_require = {
    'tests': tests_require,
    'tests_plone4': [
        'plone.formwidget.autocomplete',
        'plone.formwidget.contenttree',
     ],
    'plone': ['plone.app.testing'],
    'zope2': [
        'mechanize',
    ],
}


setup(name='ftw.testbrowser',
      version=version,
      description='A test browser for Zope and Plone.',

      long_description=open('README.rst').read() + '\n' + \
          open(os.path.join('docs', 'HISTORY.txt')).read(),

      classifiers=[
        'Framework :: Plone',
        'Framework :: Plone :: 4.3',
        'Framework :: Plone :: 5.1',
        'Framework :: Plone :: 5.2',
        'Programming Language :: Python',
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.7",
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],

      keywords='ftw browser testbrowser test',
      author='4teamwork AG',
      author_email='mailto:info@4teamwork.ch',
      url='https://github.com/4teamwork/ftw.testbrowser',

      license='GPL2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ftw', ],
      include_package_data=True,
      zip_safe=False,

      install_requires=[
        'AccessControl',
        'Acquisition',
        'cssselect',
        'lxml',
        'plone.testing',
        'plone.uuid',
        'requests',
        'requests_toolbelt',
        'setuptools',
        'six >= 1.12.0',
        'zope.component',
        'zope.deprecation',
        'zope.interface',
        'Zope2',
        ],

      tests_require=tests_require,
      extras_require=extras_require,

      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
