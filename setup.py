#!/usr/bin/env python3

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='weather-applet',
    version='1.0.0',
    author='Joerg Mechnich',
    author_email='joerg.mechnich@gmail.com',
    description='Weather system tray applet using OpenWeatherMap',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/jmechnich/weather-applet',
    packages=['weatherapplet'],
    install_requires=["appletlib"],
    scripts=['weather-applet'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        "Environment :: X11 Applications :: Qt",
    ],
    python_requires='>=3.6',
)
