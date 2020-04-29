      # -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import sys

sys.path.append('./test')

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
      packages=find_packages(),
      scripts=['bin/fsrview','bin/fsrsimulate'],
      setup_requires=['pytest-runner'],
      tests_require=['pytest'],
      long_description=readme,
      license=license
      )
