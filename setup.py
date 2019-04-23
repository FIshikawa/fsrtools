from setuptools import setup, find_packages
import sys
from fsrtools import __version__

sys.path.append('./test')

setup(name='fsrtools',
      version=__version__,
      description='F.Ishikawa made Package : manage numerical experiments',
      packages=find_packages(),
      scripts=['bin/fsrview','bin/fsrsimulate'],
      setup_requires=['pytest-runner'],
      tests_require=['pytest']
      )
