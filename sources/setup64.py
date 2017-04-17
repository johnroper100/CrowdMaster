from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import Cython.Compiler.Options
import platform

Cython.Compiler.Options.annotate = True

if platform.system() == "Linux":
    extra_compile_args = []#['-openmp']
else:
    extra_compile_args = ['/Ox','/openmp','/GT','/arch:SSE2','/fp:fast']

ext_modules = [Extension("cm_nodeFunctions", ["cm_nodeFunctions.pyx"], extra_compile_args=extra_compile_args),
               Extension("cm_soundAccel", ["cm_soundAccel.pyx"], extra_compile_args=extra_compile_args)]

setup(
  name = 'CrowdMaster',
  cmdclass = {'build_ext': build_ext},
  ext_modules = ext_modules
)
