"""ComfortableTop is distributed for Windows only."""
import sys

from setuptools import setup

if sys.platform != "win32":
    raise RuntimeError("ComfortableTop supports Windows only; Linux distribution is withdrawn")

setup()
