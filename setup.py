# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from drcs import __version__, __license__, __author__
import inspect, os

filename = inspect.getfile(inspect.currentframe())
dirpath = os.path.abspath(os.path.dirname(inspect.getfile(inspect.currentframe())))
long_description = open(os.path.join(dirpath, "README.rst")).read()

import drcs.drcs as drcs
#import drcs.converter as converter

import doctest
dirty = False
for m in [drcs]:
    failure_count, test_count = doctest.testmod(m)
    if failure_count > 0:
        dirty = True
if dirty:
    raise Exception("test failed.")

setup(name                  = 'PyDRCS',
      version               = __version__,
      description           = 'Make DRCS glyphs for DEC VT-series from image files',
      long_description      = long_description,
      py_modules            = ['drcs'],
      eager_resources       = [],
      classifiers           = ['Development Status :: 4 - Beta',
                               'Topic :: Terminals',
                               'Environment :: Console',
                               'Intended Audience :: End Users/Desktop',
                               'License :: OSI Approved :: GNU General Public License (GPL)',
                               'Programming Language :: Python'
                               ],
      keywords              = 'drcs terminal',
      author                = __author__,
      author_email          = 'user@zuse.jp',
      url                   = 'https://github.com/saitoha/PyDRCS',
      license               = __license__,
      packages              = find_packages(exclude=[]),
      zip_safe              = True,
      include_package_data  = False,
      install_requires      = ['PIL'],
      entry_points          = """
                              [console_scripts]
                              drcsconv = drcs:main
                              """
      )

