#!/usr/bin/env python

from setuptools import setup, find_packages

version = '1.0.0'

required = ['click>=6.6', 'thunder-python>=1.3.0']

setup(
    name='mesoscope',
    version=version,
    description='process data from the two-photon random access mesoscope',
    author='sofroniewn',
    author_email='the.freeman.lab@gmail.com',
    url='https://github.com/sofroniewn/mesoscope',
    packages=find_packages(),
    install_requires=required,
    entry_points = {"console_scripts": ['mesoscope = mesoscope.cli:cli']},
    long_description='See ' + 'https://github.com/sofroniewn/mesoscope',
    license='MIT'
)
