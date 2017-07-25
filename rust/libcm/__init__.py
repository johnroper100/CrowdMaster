import os
from ._interface import ffi as _ffi

_lib = _ffi.dlopen(os.path.join(os.path.dirname(__file__), '_libcm.so'))
_lib.libcm_init()

def sum(a, b):
    return _lib.sum(a,b)

def onbytes(word):
    return _lib.onbytes(word)
