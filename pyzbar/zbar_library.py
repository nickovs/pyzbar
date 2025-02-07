"""Loads zbar and its dependencies.
"""
import platform
import sys
import os

from ctypes import cdll
from ctypes.util import find_library
from pathlib import Path

__all__ = ['load']


def _windows_fnames():
    """For convenience during development and to aid debugging, the DLL names
    are specific to the bit depth of interpreter.

    This logic has its own function to make testing easier
    """
    # 'libzbar-64.dll' and 'libzbar-32.dll' each have a dependent DLL -
    # 'libiconv.dll' and 'libiconv-2.dll' respectively.
    if sys.maxsize > 2**32:
        # 64-bit
        fname = 'libzbar-64.dll'
        dependencies = ['libiconv.dll']
    else:
        # 32-bit
        fname = 'libzbar-32.dll'
        dependencies = ['libiconv-2.dll']

    return fname, dependencies


def load():
    """Loads the libzar shared library and its dependencies.
    """
    if 'Windows' == platform.system():
        # Possible scenarios here
        #   1. Run from source, DLLs are in pyzbar directory
        #       cdll.LoadLibrary() imports DLLs in repo root directory
        #   2. Wheel install into CPython installation
        #       cdll.LoadLibrary() imports DLLs in package directory
        #   3. Wheel install into virtualenv
        #       cdll.LoadLibrary() imports DLLs in package directory
        #   4. Frozen
        #       cdll.LoadLibrary() imports DLLs alongside executable
        fname, dependencies = _windows_fnames()

        def load_objects(directory):
            # Load dependencies before loading libzbar dll
            deps = [
                cdll.LoadLibrary(str(directory.joinpath(dep)))
                for dep in dependencies
            ]
            libzbar = cdll.LoadLibrary(str(directory.joinpath(fname)))
            return deps, libzbar

        try:
            dependencies, libzbar = load_objects(Path(''))
        except OSError:
            dependencies, libzbar = load_objects(Path(__file__).parent)
    else:
        # If an explicit path is set, perfer to use that
        path = os.getenv('ZBAR_PATH')
        if not path:
            # If no explicit path is set, search for the library
            path = find_library('zbar')
            if not path:
                raise ImportError(
                    'Unable to find zbar shared library. If the library '
                    'is not on the normal path, set the ZBAR_PATH environment '
                    'variable.'
                )
        libzbar = cdll.LoadLibrary(path)
        dependencies = []

    return libzbar, dependencies
