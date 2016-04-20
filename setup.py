#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()


setup(
    name='yagocd',
    version='0.1.2',
    description="Yet another Python client for ThoughtWorks GOCD REST API.",
    long_description=readme + '\n\n' + history,
    author="Grigory Chernyshev",
    author_email='systray@yandex.ru',
    url='https://github.com/grundic/yagocd',
    packages=[
        'yagocd',
    ],
    package_dir={'yagocd': 'yagocd'},
    include_package_data=True,
    license="MIT",
    zip_safe=False,
    keywords='yagocd',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
)
