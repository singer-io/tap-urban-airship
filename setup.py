#!/usr/bin/env python

from setuptools import setup, find_packages


setup(name='tap-urban-airship',
      version='0.1.0',
      description='Singer.io tap for Urban Airship data',
      author='Stitch',
      url='https://github.com/stitchstreams/tap-urban-airship',
      classifiers=['Programming Language :: Python :: 3 :: Only'],
      py_modules=['tap_urban_airship'],
      install_requires=[
          'stitchstream-python>=0.6.0',
          'requests==2.12.4',
          'backoff==1.3.2',
      ],
      entry_points='''
          [console_scripts]
          tap-urban-airship=tap_urban_airship:main
      ''',
      packages=['tap_urban_airship'],
      package_data = {
          'tap_urban_airship': [
          ],
      }
)
