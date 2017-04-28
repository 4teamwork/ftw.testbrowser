# sphinx configuration

project = u'ftw.testbrowser'
copyright = u'2013, 4teamwork GmbH'

extensions = ['sphinx.ext.autodoc']
master_doc = 'index'

from pkg_resources import get_distribution
version = release = get_distribution(project).version

import os

if 'dev' in version and os.environ.get('FOR_UPLOAD', None):
    proposal = version.split('dev', 1)[0]
    print 'The version "%s" is a dev version.' % version
    new_version = raw_input('Version to use [%s]: ' % proposal).strip()
    if not new_version:
        new_version = proposal

    version = release = new_version
    print ''
