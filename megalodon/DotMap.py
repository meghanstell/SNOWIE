#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, re, logging, json, collections, six

class DotMap(collections.abc.Mapping):
    """
        Data structure class with key/value and class attribute accessors
    """
    def __init__(self, *args: object, **kwargs: object) -> object:
        super(DotMap, self).__setattr__( '_odict', collections.OrderedDict() )
        list(map(lambda x: [self.__setattr__(kk,vv) for kk,vv in (x.items() if hasattr(x, 'items') else {}.items())], list(args) + [kwargs]))
    def __getattr__(self, key, *args, **kwargs):
        odict = super(DotMap, self).__getattribute__('_odict')
        return odict.get(key, *args, **kwargs)
    def __setattr__(self, key, val, *args, **kwargs):
        if isinstance(val, collections.abc.Mapping): return self._odict.update({key: self.__class__(val)})
        elif isinstance(val,tuple) and hasattr(val, '_asdict'):return self.__setattr__(key, val._asdict(), *args, **kwargs)
        else:return self._odict.update({key:val})
    def __iter__(self, *args, **kwargs):
        for kk in self.keys(): yield kk
    def __len__(self, *args, **kwargs): return len(self.keys())
    @property
    def __dict__(self): return self._odict
    def __setstate__(self, state):
        super(DotMap, self).__setattr__( '_odict', collections.OrderedDict() )
        self._odict.update( state )
    def __eq__(self, other): return self.__dict__ == other.__dict__
    def __ne__(self, other): return not self.__eq__(other)
    def __setitem__(self, *args, **kwargs): return self.__setattr__(*args, **kwargs)
    def __getitem__(self, *args, **kwargs): return self.__getattr__(*args, **kwargs)
    def __repr__(self):
        return json.dumps(self.__dict__, default=lambda x:x()._asdict() if hasattr(x, '_asdict') else repr(x), indent = 4)
    def __call__(self, *args, **kwargs):
        if args and isinstance(args[0], collections.abc.Mapping):
            [self.__setattr__(kk,vv) for kk,vv in args[0].items()]
        [self.__setattr__(kk,vv) for kk,vv in kwargs.items()]
        return self

    def _asjson(self): return json.dumps(self._asdict(), indent=4)
    def _asdict(self): return collections.OrderedDict([(kk, vv._asdict() if hasattr(vv,'_asdict') else vv) for kk,vv in self.__dict__.items()])
    def __format__(self, spec, *args, **kwargs):
        if 'json' in spec.lower(): return self._asjson()
        return super(DotMap, self).__format__(spec, *args, **kwargs)
    def pop(self, *args, **kwargs): return self.__dict__.pop(*args, **kwargs)
    def items(self, *args, **kwargs): return self.__dict__.items(*args, **kwargs)
    def keys(self, *args, **kwargs): return self.__dict__.keys(*args, **kwargs)
    def get(self, name, *args, **kwargs): return self.__getattr__(name, *args, **kwargs)
    def values(self, *args, **kwargs): return self.__dict__.values(*args, **kwargs)
    def setdefault(self, *args, **kwargs): return self.__dict__.setdefault(*args, **kwargs)
    def match(self,key_val, *args, **kwargs): return [result for result in self.imatch(key_val, *args, **kwargs)]
    def imatch(self, key_val, *args, **kwargs):
        key,val=key_val
        maintain_structure=kwargs.get('maintain_structure',False)
        def _yield(dd=self):
            if isinstance(dd, collections.abc.Mapping):
                for kk,vv in dd.items():
                    if isinstance(vv,six.string_types):
                        if all([re.match(key,kk),re.match(val,vv)]):
                            yield dd
                    else:
                        for _match in _yield(vv):
                            if maintain_structure:
                                yield self.__class__(dict(dd, **{kk:_match}))
                            else:
                                yield _match
            elif isinstance(dd, (list,tuple)):
                for ii in dd:
                    for _match in _yield(ii): yield _match
            elif isinstance(dd,six.string_types): pass
            else: print('Unhandled Type: {}'.format(type(dd)))
        for result in _yield(): yield result

    def find(self, *keys, **kwargs): return [result for result in self.ifind(*keys, **kwargs)]
    def ifind(self, *keys, **kwargs):
        maintain_structure=kwargs.get('maintain_structure',False)
        def _yield(dd=self):
            for kk,vv in dd.items():
                if kk in keys:
                    if maintain_structure: yield self.__class__({kk:vv})
                    else: yield self.__class__(vv) if isinstance(vv, collections.abc.Mapping) else vv
                if isinstance(vv,collections.abc.Mapping):
                    for _match in _yield(vv):
                        if maintain_structure: yield self.__class__({kk:_match})
                        else: yield _match
        for result in _yield(): yield result
    def refind(self, *keys, **kwargs): return [result for result in self.irefind(*keys, **kwargs)]
    def irefind(self, *keys, **kwargs):
        maintain_structure=kwargs.get('maintain_structure',False)
        flags=kwargs.pop('flags',0)
        def _yield(dd=self):
            for kk,vv in dd.items():
                if any([re.match(_key, kk, flags=flags) for _key in keys]):
                    if maintain_structure: yield self.__class__({kk:vv})
                    else: yield self.__class__(vv) if isinstance(vv, collections.abc.Mapping) else vv
                if isinstance(vv,collections.abc.Mapping):
                    for _match in _yield(vv):
                        if maintain_structure: yield self.__class__({kk:_match})
                        else: yield _match
        for result in _yield(): yield result
    def update(self, *args, **kwargs):
        [self.__setattr__(kk,vv) for arg in args for kk,vv in arg.items() if isinstance(arg, collections.abc.Mapping)]
        [self.__setattr__(kk,vv) for kk,vv in kwargs.items()]
        return self
    def merge(self, other, *args, **kwargs):
        if not isinstance(other, collections.abc.Mapping): raise RuntimeError("Attempting to merge DotMap with type {}... i dunno how to do that".format(type(other)))
        def _update(_d, _u):
            [_d.__setitem__(kk, (_update(_d.get(kk, {}), vv) if isinstance(vv, collections.abc.Mapping) else vv)) for kk,vv in _u.items()]
            return _d
        _update(self.__dict__, other)
        return self

class SmartDict(DotMap):
    def __setattr__(self, name, value): return super(SmartDict, self).__setattr__(name, value) if value is not(None) else None

def test():
    dm=DotMap(collections.OrderedDict([('a',1),('b',2),('c',collections.OrderedDict([('d',4),('e',5)]))]))
    _dm=DotMap(collections.OrderedDict([('a',2),('f',2),('c',collections.OrderedDict([('d',7)])), ('g',collections.OrderedDict([('d',4),('e',5)]))]))
    _dmm=DotMap(collections.OrderedDict([('h',2),('i',2),('j',collections.OrderedDict([('k',7)])), ('l',collections.OrderedDict([('m',4),('n',5)]))]))
    _dms=[dm, _dm, _dmm]

    print('{:json}'.format(dm))
    print('{:json}'.format(_dm))
    dm.merge(_dm)
    print('{:json}'.format(dm))
    [print('{}: {}'.format(kk,vv)) for kk,vv in dm.items()]
    print('dm.c.d: {}'.format(dm.c.d))

def main():
    test()

if __name__ == '__main__':
    main()

################################################################################
# vim:set sr et ts=4 sw=4 ft=python fenc=utf-8: // See Vim, :help 'modeline'
