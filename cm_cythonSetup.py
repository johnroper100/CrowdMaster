from distutils.core import setup
from Cython.Build import cythonize

setup(
    name = "C_cm_nodeFunctions",
    ext_modules = cythonize("C_cm_nodeFunctions.pyx")
)
