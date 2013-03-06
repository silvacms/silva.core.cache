# -*- coding: utf-8 -*-
# Copyright (c) 2008-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from setuptools import setup, find_packages
import os

version = '3.0.2'

tests_require = [
    'infrae.testing',
    ]

setup(name='silva.core.cache',
      version=version,
      description="caching utils for Silva",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
          "Environment :: Web Environment",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: Zope Public License",
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Framework :: Zope2",
          ],
      keywords='zope2 cache silva',
      author='Infrae',
      author_email='info@infrae.com',
      url='https://hg.infrae.com/silva',
      license='BSD',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      namespace_packages=['silva', 'silva.core'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'Beaker',
        'five.grok',
        'infrae.cache',
        'python-memcached',
        'setuptools',
        'silva.core.views',
        'zope.component',
        'zope.datetime',
        'zope.interface',
        'zope.publisher',
        'zope.session',
        ],
      tests_require = tests_require,
      extras_require = {'test': tests_require},
      )
