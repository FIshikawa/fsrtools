from setuptools import setup, find_packages
import sys

sys.path.append('./test')

setup(
      packages=find_packages(),
      scripts=['bin/fsrview','bin/fsrsimulate'],
      setup_requires=['pytest-runner'],
      tests_require=['pytest']
      )
