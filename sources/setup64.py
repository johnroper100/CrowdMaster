from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import Cython.Compiler.Options
import platform

Cython.Compiler.Options.annotate = True

if platform.system() != "Windows":
    extra_compile_args = []#['-openmp']
else:
    extra_compile_args = ['/Ox','/openmp','/GT','/arch:SSE2','/fp:fast']

ext_modules = [Extension("cm_accelerate", ["cm_accelerate.pyx"], extra_compile_args=extra_compile_args), Extension("cm_compileBrain", ["cm_compileBrain.pyx"], extra_compile_args=extra_compile_args)]

setup(
  name = 'CrowdMaster',
  cmdclass = {'build_ext': build_ext},
  ext_modules = ext_modules
)
