# -*- coding: utf-8 -*-

"""
Author:        Wang Chao <yueyoum@gmail.com>
Filename:      setup.py
Date created:  2016-09-29 11:04:20
Description:

"""

from setuptools import setup

setup(
    name='protoext',
    version='0.1.0',
    packages=['protoext'],
    url='https://github.com/yueyoum/protoext',
    license='',
    author='Yueyoum',
    author_email='yueyoum@gmail.com',
    description='',
    entry_points={
        'console_scripts': [
            'protoext = protoext.gen.protoext',
            'protoext_python = protoext.gen.protoext_python',
            'protoext_erlang = protoext.gen.protoext_erlang',
            ]
        }
)
