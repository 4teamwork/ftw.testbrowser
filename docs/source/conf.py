# sphinx configuration

project = u'ftw.testbrowser'
copyright = u'2013, 4teamwork GmbH'

extensions = ['sphinx.ext.autodoc']
master_doc = 'index'

from pkg_resources import get_distribution
version = release = get_distribution(project).version
