#!/usr/bin/python

from distutils.core import setup

setup(name='turnin-ng',
      version='0.1_pre-alpha',
      description='Turn in your assignments with turnin',
      author='Ryan Kavanagh',
      author_email='ryanakca@kubuntu.org',
      scripts=['src/project.py', 'src/turnin.py'],
      packages=['turnin'],
      package_dir={'turnin':'src/turnin'},
)
