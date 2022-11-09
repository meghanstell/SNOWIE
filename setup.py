#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)
import os, re, pathlib
from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext as build_ext_orig

def get_files(root, pattern=None, ignore=None):
    _files=[]
    for root, dirs, files in os.walk(root):
        for file in files:
            if pattern and not(re.match(pattern, file)): continue
            if ignore and any([re.match(_ignore, os.sep.join([root,file])) for _ignore in ignore]): continue
            _files.append(os.sep.join([root,file]))
    return _files

def get_dependencies(req_file=None):
    if os.path.isfile(req_file if req_file else os.path.join(os.path.dirname(__file__),'requirements.txt')):
        with open(req_file, 'r') as rr: return filter(lambda x: bool(x), [_rr.strip() for _rr in rr.readlines()])

setup(
    name = 'megalodon',
    version = '1.0.0',
    url = 'https://github.com/meghanstell/megalodon',
    author = 'Meghan Stell',
    author_email = 'Meghan.H.Stell@gmail.com',
    description = "A big shark! With nasty sharp pointy teeth",
    data_files = [
        ('bin',get_files('bin')),
        ('config',get_files('config')),
        ('doc',get_files('doc')),
        ('lib',get_files('lib')),
        ('notes',get_files('notes')),
        ('test',get_files('test')),],
    packages = find_packages(),
    include_package_data=True,
    install_requires = [],
    entry_points='''
        [console_scripts]
        meg=megalodon.cli:_meg
    '''
)
