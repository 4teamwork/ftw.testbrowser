#!/usr/bin/env python

import os
import re

print 'Copy all eggs from bin/sphinx-build script to rtd-requirements.txt.'

sphinx_build_path = os.path.abspath(os.path.join(__file__, '..', 'bin', 'sphinx-build'))
requirements_path = os.path.abspath(os.path.join(__file__, '..', 'rtd-requirements.txt'))

requirements = []

with open(sphinx_build_path, 'r') as sphinx_build_fio:
   for line in sphinx_build_fio:
       match = re.match(r'^ +\'.*?/eggs/([^-]+)-(.*?)-py[\d.]*\.egg\',$', line)
       if match:
          requirements.append(match.groups())


with open(requirements_path, 'w+') as requirements_fio:
   for name, version in requirements:
      requirements_fio.write('{} == {}\n'.format(name, version))

print 'Updated.'
