#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)
import os, sys, stat, re, json, yaml, collections, getpass, functools, six, pkg_resources, importlib, traceback, logging, datetime, six, bcrypt, threading, numbers, socket, types
import rich_click as click
from enum import Enum
import sqlalchemy as sa

_logger_format_args = dict(level=os.environ.get('MEG_LOGLEVEL', 'INFO'), format=" [%(name)s] :: %(message)s", datefmt="[%X] ")


from rich.traceback import install
install()

from rich.logging import RichHandler
_logger_format_args.update(dict(handlers=[RichHandler()]))

from rich.console import Console
from rich.syntax import Syntax
from rich.table import (Column, Table)

logging.basicConfig(**_logger_format_args)

# from .DotMap import (DotMap, SmartDict)
# from .Environment import Environment
# from .NamedTuple import NamedTuple
# from .ThreadPool import ThreadPool


def chmod(*paths, mode=None):
    mode=mode if mode else 0o0775
    _umask = os.umask(0)
    def _ch(path): return os.chmod(path, mode) if path and os.path.exists(path) else None
    try:
        list(map(_ch, paths))
    finally:
        os.umask(_umask)
        return paths[0] if (len(paths)==1) else paths

def makedirs(*dirs, mode=None):
    mode=mode if mode else 0o7775
    _umask = os.umask(0)
    # _mode = 0o7775 # stat.S_ISUID|stat.S_ISGID|stat.S_IRWXU|stat.S_IRWXG|stat.S_IRWXO
    def _mk(_dir):
        _placeholder=os.path.join(_dir, '.dockerignore')
        _=chmod(_dir, mode=mode) if os.path.exists(_dir) else os.makedirs(_dir, mode)
        with open(_placeholder, 'a'): pass
        chmod(_placeholder, mode=mode)
    try:
        list(map(_mk, dirs))
    finally:
        os.umask(_umask)
        return dirs[0] if (len(dirs)==1) else dirs

class Base(object):
    @property
    def _qualname(self):
        if self.__qualname is None:
            module = self.__class__.__module__
            self._qualname=self.__class__.__name__  if ((module is(None)) or (module == str.__class__.__module__)) else '.'.join([module, self.__class__.__name__])
        return self.__qualname
    @_qualname.setter
    def _qualname(self, value): self.__qualname = value

    @property
    def logger(self):
        if self._logger is None: self.logger = logging.getLogger(self._qualname)
        return self._logger
    @logger.setter
    def logger(self, value):
        if isinstance(value, six.string_types): return
        self._logger=value

    @property
    def ignore_keys(self):
        if self._ignore_keys is None: self.ignore_keys = ['ignore_keys', 'logger']
        return self._ignore_keys
    @ignore_keys.setter
    def ignore_keys(self, value): self._ignore_keys=value

    def __init__(self, *args, **kwargs): [self.__setattr__(kk,vv) for kk,vv in kwargs.items()]
    def __call__(self, *args, **kwargs):
        [self.__setattr__(kk,vv) for kk,vv in kwargs.items()]
        return self
    def __getattr__(self, name): return self.__dict__.get(name, None)
    def _asdict(self, ignore=None):
        if isinstance(ignore, six.string_types): ignore=[ignore]
        if ignore is(None): ignore=[]
        _props = list(filter(lambda x: isinstance(getattr(self.__class__,x),property), dir(self.__class__)))
        _keys = list(filter(lambda x: not(x.startswith('_')), self.__dict__.keys()))
        _dd=collections.OrderedDict([(kk,getattr(self, kk)) for kk in sorted(list(set(_keys + _props) - set(self.ignore_keys + ignore)))])
        def _yield(obj):
            if hasattr(obj, '_asdict'):
                if isinstance(obj, tuple):
                    return collections.OrderedDict([(kk,_yield(vv)) for kk,vv in obj._asdict().items()])
                else:
                    return obj._asdict()
            if isinstance(obj, collections.abc.Mapping): return collections.OrderedDict([(kk,_yield(vv)) for kk,vv in obj.items()])
            elif isinstance(obj, list): return [_yield(_obj) for _obj in obj]
            elif isinstance(obj, types.MethodType): return None
            elif isinstance(obj, Enum): return {'{}.{}'.format(obj.__class__.__name__, obj.name):obj.value}
            elif isinstance(obj, threading.Event): return None
            elif isinstance(obj, (datetime.datetime, datetime.timedelta)): return '{}'.format(obj)
            elif isinstance(obj, bytes): return obj.decode('utf8')
            else: return obj
        __dd = collections.OrderedDict([(kk, _yield(vv) ) for kk,vv in _dd.items() if ( (vv is not(None)) and ( not(kk.startswith('_')) ) ) ])
        return __dd
    def _asjson(self): return json.dumps(self._asdict(), indent=4)
    def __format__(self, spec): return '{}'.format(self._asjson())
    def show(self):
        Console().print(Syntax('{}'.format(self), "json", theme="monokai"))
        return self

    def chmod(self, *paths): return chmod(*paths)
    def makedirs(self, *dirs): return makedirs(*dirs)

class MegContext(Base):
    @property
    def meg_host(self):
        if self._meg_host is None:
            self.meg_host = os.environ.get('MEG_HOST','0.0.0.0')
        return self._meg_host
    @meg_host.setter
    def meg_host(self, value):
        self._meg_host = value

    @property
    def meg_port(self):
        if self._meg_port is None:
            self.meg_port = os.environ.get('MEG_PORT', 5900)
        return self._meg_port
    @meg_port.setter
    def meg_port(self, value):
        self._meg_port = int(value)
