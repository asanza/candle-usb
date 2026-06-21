#!/usr/bin/env python
import io
import os

from setuptools import find_packages, setup

NAME        = "candle-usb"
DESCRIPTION = "Python CAN / CAN FD driver for candleLight USB adapters and Geschwister Schneider gs_usb devices (Windows, Linux, macOS)."
URL         = "https://github.com/diegoasanza/candle-usb"
EMAIL       = "f.asanza@gmail.com"
AUTHOR      = "Diego Asanza"

here = os.path.abspath(os.path.dirname(__file__))

try:
    with io.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
        long_description = "\n" + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

about = {}
with open(os.path.join(here, "candle_usb", "__version__.py")) as f:
    exec(f.read(), about)

setup(
    name=NAME,
    version=about["__version__"],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    install_requires=["pyusb>=1.0.2"],
    include_package_data=True,
    license="MIT",
    entry_points={
        "console_scripts": [
            "pycandump=candle_usb.pycandump:main",
        ],
    },
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: System :: Hardware :: Hardware Drivers",
    ],
)
