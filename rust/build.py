import sys
import subprocess
from cffi import FFI


def _to_source(x):
    if sys.version_info >= (3, 0) and isinstance(x, bytes):
        x = x.decode('utf-8')
    return x


ffi = FFI()
ffi.cdef(_to_source(subprocess.Popen([
    'cc', '-E', 'include/libcm.h'],
    stdout=subprocess.PIPE).communicate()[0]))
ffi.set_source('libcm._interface', None)

