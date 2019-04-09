from setuptools import setup, find_packages
from fsrtools import __version__

setup(name='fsrtools',
      version=__version__,
      description='F.Ishikawa made Package : manage numerical experiments',
      packages=find_packages(),
      scripts=['bin/fsrview','bin/fsrsimulate']
      )
