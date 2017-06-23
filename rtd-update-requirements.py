#!/usr/bin/env python

import os
import re

print 'Copy all eggs from bin/sphinx-build script to rtd-requirements.txt.'

sphinx_build_path = os.path.abspath(os.path.join(__file__, '..', 'bin', 'sphinx-build'))
requirements_path = os.path.abspath(os.path.join(__file__, '..', 'rtd-requirements.txt'))

requirements = []

with open(sphinx_build_path, 'r') as sphinx_build_fio:
   for line in sphinx_build_fio:
      match = re.match(r'^ +\'.*?/eggs/([^-]+)-(.*?)-py[\d.]*(?:-.+?)?\.egg\',$', line)
      if match:
         requirements.append(match.groups())
      else:
         print 'XX', repr(line)


# These are the eggs that are installed by read the docs. Rtd installs specific
# versions. When we install other versions it may not work with the commands
# rtd runs. Therefore we must not pin those packages.
# Copied form the build's "pip install".
rtd_eggs = map(str.lower, map(str.strip, (
   'six, idna, urllib3, chardet, certifi, requests, docutils,'
   ' Pygments, imagesize, pytz, babel, snowballstemmer, MarkupSafe,'
   ' Jinja2, alabaster, sphinx, singledispatch, backports-abc, tornado,'
   ' click, livereload, mkdocs-bootstrap, mkdocs-bootswatch, PyYAML,'
   ' Markdown, mkdocs, mock, pillow, nilsimsa, readthedocs-sphinx-ext,'
   ' sphinx-rtd-theme, commonmark, recommonmark').split(',')))

with open(requirements_path, 'w+') as requirements_fio:
   for name, version in requirements:
      if name.lower() in rtd_eggs:
         continue
      requirements_fio.write('{} == {}\n'.format(name, version))

print 'Updated.'
