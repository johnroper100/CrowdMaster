import os
import sys
import shutil
import subprocess

try:
    from wheel.bdist_wheel import bdist_wheel
except ImportError:
    bdist_wheel = None

from setuptools import setup, find_packages
from distutils.command.build_py import build_py
from distutils.command.build_ext import build_ext
from setuptools.dist import Distribution


# Build with clang if not otherwise specified.
if os.environ.get('LIBCM_MANYLINUX') == '1':
    os.environ.setdefault('CC', 'gcc')
    os.environ.setdefault('CXX', 'g++')
else:
    os.environ.setdefault('CC', 'clang')
    os.environ.setdefault('CXX', 'clang++')


PACKAGE = 'libcm'
EXT_EXT = sys.platform == 'darwin' and '.dylib' or '.so'


def build_libcm(base_path):
    lib_path = os.path.join(base_path, '_libcm.so')
    here = os.path.abspath(os.path.dirname(__file__))
    cmdline = ['cargo', 'build', '--release']
    if not sys.stdout.isatty():
        cmdline.append('--color=always')
    rv = subprocess.Popen(cmdline, cwd=here).wait()
    if rv != 0:
        sys.exit(rv)
    src_path = os.path.join(here, 'target', 'release',
                            'liblibcm' + EXT_EXT)
    if os.path.isfile(src_path):
        shutil.copy2(src_path, lib_path)


class CustomBuildPy(build_py):
    def run(self):
        build_py.run(self)
        build_libcm(os.path.join(self.build_lib, *PACKAGE.split('.')))


class CustomBuildExt(build_ext):
    def run(self):
        build_ext.run(self)
        if self.inplace:
            build_py = self.get_finalized_command('build_py')
            build_libcm(build_py.get_package_dir(PACKAGE))


class BinaryDistribution(Distribution):
    """This is necessary because otherwise the wheel does not know that
    we have non pure information.
    """
    def has_ext_modules(foo):
        return True


cmdclass = {
    'build_ext': CustomBuildExt,
    'build_py': CustomBuildPy,
}


# The wheel generated carries a python unicode ABI tag.  We want to remove
# this since our wheel is actually universal as far as this goes since we
# never actually link against libpython.  Since there does not appear to
# be an API to do that, we just patch the internal function that wheel uses.
if bdist_wheel is not None:
    class CustomBdistWheel(bdist_wheel):
        def get_tag(self):
            rv = bdist_wheel.get_tag(self)
            return ('py2.py3', 'none') + rv[2:]
    cmdclass['bdist_wheel'] = CustomBdistWheel


setup(
    name='libcm',
    version='0.1.0',
    url='https://github.com/johnroper100/CrowdMaster',
    description='Used to accelerate CrowdMaster',
    author='Peter Noble',
    author_email='peter@noblesque.org.uk',
    packages=find_packages(),
    cffi_modules=['build.py:ffi'],
    cmdclass=cmdclass,
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        'cffi>=1.10.0',
    ],
    setup_requires=[
        'cffi>=1.10.0'
    ],
    ext_modules=[],
    distclass=BinaryDistribution
)

