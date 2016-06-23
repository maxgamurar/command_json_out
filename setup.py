# -*- coding: utf-8 -*-
# Copyright (c) 2016, Maxim Gamurar <max@v-integ.com>
# License: BSD

import sys
import os
import re
import command_json_out

from setuptools import setup, find_packages


with open('README.rst') as stream:
    long_desc = stream.read()


setup(
    name='command_json_out',
    version=command_json_out.__version__,
    url='https://github.com/maxgamurar/command_json_out',
    license='BSD',
    author='Maxim Gamurar',
    author_email='max@v-integ.com',
    description='Sphinx extension to parse anaconda-cloud JSON command help output with markdown info into DL HTML',
    long_description=long_desc,
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Documentation',
        'Topic :: Utilities',
    ],
    platforms='any',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['Sphinx>=1.1', 'markdown']
)
