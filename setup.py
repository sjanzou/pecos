from setuptools import setup, find_packages
from distutils.core import Extension

DISTNAME = 'pecos'
VERSION = '0.1'
PACKAGES = ['pecos']
EXTENSIONS = []
DESCRIPTION = 'Python package for performance monitoring of time series data.'
LONG_DESCRIPTION = open('README.md').read()
AUTHOR = 'Katherine Klise, Joshua Stein'
MAINTAINER_EMAIL = 'kaklise@sandia.gov'
LICENSE = 'Revised BSD'
URL = 'https://github.com/kaklise/pecos'

setup(name=DISTNAME,
      version=VERSION,
      packages=PACKAGES,
      ext_modules=EXTENSIONS,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      author=AUTHOR,
      maintainer_email=MAINTAINER_EMAIL,
      license=LICENSE,
      url=URL,
      zip_safe=False)
