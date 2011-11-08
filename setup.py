# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: setup.py 44106 2010-07-29 11:12:54Z sylvain $

from setuptools import setup, find_packages
import os

version = '3.0.1dev'

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
      license='ZPL',
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
        'zope.testing',
        ],
      tests_require = tests_require,
      extras_require = {'test': tests_require},
      )
