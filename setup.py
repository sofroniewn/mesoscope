#!/usr/bin/env python

from setuptools import setup, find_packages

version = '1.0.3'

required = ['click>=6.6', 'thunder-python>=1.4.2', 'thunder-registration>=1.0.1', 'showit>=1.1.1',
            'thunder-extraction>=1.2.1', 'neurofinder>=1.1.1']

setup(
    name='mesoscope',
    version=version,
    description='process data from the two-photon random access mesoscope',
    author='sofroniewn',
    author_email='sofroniewn@gmail.com',
    url='https://github.com/sofroniewn/mesoscope',
    packages=find_packages(),
    install_requires=required,
    entry_points = {"console_scripts": ['mesoscope = mesoscope.cli:cli']},
    long_description='See ' + 'https://github.com/sofroniewn/mesoscope',
    license='MIT'
)
