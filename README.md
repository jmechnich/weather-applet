[![PyPI versio](https://img.shields.io/pypi/v/weather-applet)](https://pypi.org/project/weather-applet/)
[![PyPi format](https://img.shields.io/pypi/format/weather-applet)](https://pypi.org/project/weather-applet/)
[![PyPI license](https://img.shields.io/pypi/l/weather-applet)](https://pypi.org/project/weather-applet/)
[![PyPi weekly downloads](https://img.shields.io/pypi/dw/weather-applet)](https://pypi.org/project/weather-applet/)

weather-applet
==============

Weather system tray applet for X11, written in Python 3 and PyQt 5. An
API key from https://openweathermap.org/ is required.

Functionality
=============

- Shows system tray icon displaying current weather icon and
  temperature
- Left single- or double-click toggles splash screen with weather info
  for now, today, tomorrow or the week
- Middle-click triggers icon reset
- Location can be selected automatically, by name, by OWM id or by
  coordinates

Requirements
============

- appletlib (https://github.com/jmechnich/appletlib)
- Python 3
- PyQt 5

Screenshots
===========

#### Splash screen showing today's weather
![](https://raw.github.com/jmechnich/weather-applet/master/misc/screenshot.png)
