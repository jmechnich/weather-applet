#!/usr/bin/env python3

from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='weather-applet',
    author='Joerg Mechnich',
    author_email='joerg.mechnich@gmail.com',
    description='Weather system tray applet using OpenWeatherMap',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/jmechnich/weather-applet',
    packages=['weatherapplet'],
    use_scm_version={"local_scheme": "no-local-version"},
    setup_requires=['setuptools_scm'],
    install_requires=["appletlib"],
    scripts=['weather-applet'],
    data_files = [
        ('share/applications', ['weather-applet.desktop']),
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        "Environment :: X11 Applications :: Qt",
    ],
    python_requires='>=3.6',
)
