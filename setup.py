#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import codecs

from setuptools import setup, find_packages


VERSION = ''
with open('xd/__version__.py', 'r') as f:
    VERSION = re.search(
        r'__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
        f.read(), re.M
    ).group(1)

if not VERSION:
    raise RuntimeError('Cannot find version information')

with codecs.open('README.rst', encoding='utf-8') as f:
    README = f.read()

# Integrate with Pipfile?
REQUIRES = [
    'colorama',
    'click',
    'requests',
    'six>=1.11.0',
    'pyyaml',
    'pytoml',
    'configparser',
]


setup(
    name='xd',
    version=VERSION,
    description='a list of useful commands which makes life easier',
    long_description=README,
    url='https://github.com/damnever/xd',
    author='damnever',
    author_email='dxc.wolf@gmail.com',
    license='The BSD 3-Clause License',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='command line tools',
    packages=find_packages(),
    install_requires=REQUIRES,
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'xd=xd.__main__:xd',
        ]
    },
)
