from appletlib.splash import Splash

from weatherapplet.utils import Modes

import time, syslog

from PyQt6.QtCore import Qt
from PyQt6.QtGui import (
    QFont,
    QFontMetrics,
    QPainter,
    QPixmap,
)


class SplashWeather(Splash):
    def __init__(self, indicator):
        super(SplashWeather, self).__init__()
        self.i = indicator
        self.initVars()
        self.updateSplash()

    def initVars(self):
        self.margin = 2
        self.w = 200
        self.h = 250
        self.lineh = 15

    def updateSplash(self):
        self.fitContents()
        self.update()

    def fitContents(self):
        if not self.i.data or not len(self.i.data):
            self.w = 150
            self.h = self.lineh
        else:
            items = 12
            self.w = 300
            self.h = 50 + (self.lineh + self.margin) * items
        self.resize(self.w, self.h)

    def wheelEvent(self, ev):
        ev.accept()
        self.i.cycleMode(ev.angleDelta().y())

    def paintEvent(self, ev):
        ev.accept()
        self.fitContents()
        p = QPainter(self)
        p.setFont(self.font)
        p.fillRect(self.rect(), self.i.systray.bgColor)
        p.setPen(self.i.systray.fgColor)
        p.translate(self.margin, self.margin)
        data = self.i.data
        if not data or not len(data):
            p.drawText(
                0, 0, self.w, self.h, Qt.AlignmentFlag.AlignCenter, "No data available"
            )
            p.end()
            return
        self.drawHeader(p)
        if self.i.mode == Modes.Now:
            self.drawWeather(p)
        elif self.i.mode == Modes.Today:
            self.drawDay(p)
        elif self.i.mode == Modes.Tomorrow:
            self.drawDay(p, prefix="tomorrow")
        elif self.i.mode == Modes.Week:
            self.drawWeek(p)

    def drawDay(self, p, prefix="today"):
        syslog.syslog(syslog.LOG_DEBUG, "DEBUG  weather_splash drawDay")
        p.save()
        iconoff = 50
        hdrw = 45
        y = iconoff + self.margin
        p.setFont(self.font)
        p.drawText(
            0, round(y), hdrw, round(self.lineh), Qt.AlignmentFlag.AlignCenter, "Time"
        )
        y += self.lineh + self.margin
        p.drawText(
            0, round(y), hdrw, round(self.lineh), Qt.AlignmentFlag.AlignCenter, "Status"
        )
        y += self.lineh + self.margin
        y += self.lineh + self.margin
        p.drawText(
            0, round(y), hdrw, round(self.lineh), Qt.AlignmentFlag.AlignCenter, "Temp"
        )
        y += self.lineh + self.margin
        p.drawText(
            0, round(y), hdrw, round(self.lineh), Qt.AlignmentFlag.AlignCenter, "Min"
        )
        y += self.lineh + self.margin
        p.drawText(
            0, round(y), hdrw, round(self.lineh), Qt.AlignmentFlag.AlignCenter, "Max"
        )
        y += self.lineh + self.margin
        p.drawText(
            0, round(y), hdrw, round(self.lineh), Qt.AlignmentFlag.AlignCenter, "Wind"
        )
        y += self.lineh + self.margin
        p.drawText(
            0,
            round(y),
            hdrw,
            round(self.lineh),
            Qt.AlignmentFlag.AlignCenter,
            "Rain/3h",
        )
        p.translate(hdrw, 0)
        for i in range(5):
            hour = "%s%d" % (prefix, i)
            if not hour in self.i.data:
                break
            data = self.i.data[hour]
            icon = QPixmap(self.i.iconPath(data["icon"]))
            y = 0
            p.drawPixmap(0, round(y), icon.width(), icon.height(), icon)
            y += icon.height() + self.margin
            p.drawText(
                0,
                round(y),
                icon.width(),
                round(self.lineh),
                Qt.AlignmentFlag.AlignCenter,
                time.strftime("%H:%M", time.localtime(data["time"])),
            )
            y += self.lineh + self.margin
            p.drawText(
                0,
                round(y),
                icon.width(),
                round(self.lineh),
                Qt.AlignmentFlag.AlignCenter,
                str(data["status"]),
            )
            y += self.lineh + self.margin
            y += self.lineh + self.margin
            p.drawText(
                0,
                round(y),
                icon.width(),
                round(self.lineh),
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight,
                "%.1f \xb0C" % data["temp"],
            )
            y += self.lineh + self.margin
            p.drawText(
                0,
                round(y),
                icon.width(),
                round(self.lineh),
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight,
                "%.1f \xb0C" % data["temp_min"],
            )
            y += self.lineh + self.margin
            p.drawText(
                0,
                round(y),
                icon.width(),
                round(self.lineh),
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight,
                "%.1f \xb0C" % data["temp_max"],
            )
            y += self.lineh + self.margin
            p.drawText(
                0,
                round(y),
                icon.width(),
                round(self.lineh),
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight,
                "%.1f m/s" % data.get("wind_speed", 0),
            )
            y += self.lineh + self.margin
            p.drawText(
                0,
                round(y),
                icon.width(),
                round(self.lineh),
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight,
                "%d mm" % data.get("rain_3h", 0),
            )
            p.translate(icon.width(), 0)
        p.restore()

    def drawWeek(self, p):
        syslog.syslog(syslog.LOG_DEBUG, "DEBUG  weather_splash drawWeek")
        p.save()
        iconoff = 50
        hdrw = 45
        y = iconoff + self.margin
        p.setFont(self.font)
        y += self.lineh + self.margin
        p.drawText(
            0, round(y), hdrw, round(self.lineh), Qt.AlignmentFlag.AlignCenter, "Date"
        )
        y += self.lineh + self.margin
        p.drawText(
            0, round(y), hdrw, round(self.lineh), Qt.AlignmentFlag.AlignCenter, "Status"
        )
        y += self.lineh + self.margin
        y += self.lineh + self.margin
        p.drawText(
            0,
            round(y),
            hdrw,
            round(self.lineh),
            Qt.AlignmentFlag.AlignCenter,
            "Morning",
        )
        y += self.lineh + self.margin
        p.drawText(
            0, round(y), hdrw, round(self.lineh), Qt.AlignmentFlag.AlignCenter, "Day"
        )
        y += self.lineh + self.margin
        p.drawText(
            0, round(y), hdrw, round(self.lineh), Qt.AlignmentFlag.AlignCenter, "Eve"
        )
        y += self.lineh + self.margin
        p.drawText(
            0, round(y), hdrw, round(self.lineh), Qt.AlignmentFlag.AlignCenter, "Night"
        )
        p.translate(hdrw, 0)
        for i in range(5):
            day = "daily%d" % i
            if not day in self.i.data:
                break
            data = self.i.data[day]
            icon = QPixmap(self.i.iconPath(data["icon"]))
            y = 0
            p.drawPixmap(0, round(y), icon.width(), icon.height(), icon)
            y += icon.height()
            p.drawText(
                0,
                round(y),
                icon.width(),
                round(self.lineh),
                Qt.AlignmentFlag.AlignCenter,
                "%s" % time.strftime("%a", time.localtime(data["time"])),
            )
            y += self.lineh + self.margin * 2
            p.drawText(
                0,
                round(y),
                icon.width(),
                round(self.lineh),
                Qt.AlignmentFlag.AlignCenter,
                "%s" % time.strftime("%h %d", time.localtime(data["time"])),
            )
            y += self.lineh + self.margin
            p.drawText(
                0,
                round(y),
                icon.width(),
                round(self.lineh),
                Qt.AlignmentFlag.AlignCenter,
                "%s" % data["status"],
            )
            y += self.lineh + self.margin
            y += self.lineh + self.margin
            p.drawText(
                0,
                round(y),
                icon.width(),
                round(self.lineh),
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight,
                "%.1f \xb0C" % data["temp_morn"],
            )
            y += self.lineh + self.margin
            p.drawText(
                0,
                round(y),
                icon.width(),
                round(self.lineh),
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight,
                "%.1f \xb0C" % data["temp_day"],
            )
            y += self.lineh + self.margin
            p.drawText(
                0,
                round(y),
                icon.width(),
                round(self.lineh),
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight,
                "%.1f \xb0C" % data["temp_eve"],
            )
            y += self.lineh + self.margin
            p.drawText(
                0,
                round(y),
                icon.width(),
                round(self.lineh),
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight,
                "%.1f \xb0C" % data["temp_night"],
            )
            p.translate(icon.width(), 0)
        p.restore()

    def drawItem(self, p, center, title, value):
        p.drawText(
            0,
            0,
            round(center),
            round(self.lineh),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            title,
        )
        p.drawText(
            round(center),
            0,
            round(center),
            round(self.lineh),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            value,
        )
        p.translate(0, round(self.lineh + self.margin))

    def drawHeader(self, p):
        syslog.syslog(syslog.LOG_DEBUG, "DEBUG  weather_splash drawHeader")
        data = self.i.data
        w = self.w - 2 * self.margin
        h = self.h - 2 * self.margin

        iconname = "icon"
        if iconname in data:
            pass
        elif "icon_0" in data:
            iconname = "icon_0"
        else:
            syslog.syslog(syslog.LOG_WARNING, "WARN  drawHeader no icon")
            syslog.syslog(syslog.LOG_DEBUG, repr(data.keys()))
        icon = QPixmap(self.i.iconPath(data[iconname]))
        p.drawPixmap(0, 0, icon.width(), icon.height(), icon)

        name = data["name"]
        if len(data["country"]):
            name += ", " + data["country"]
        f = QFont(self.font)
        fs = 12
        while True:
            f.setPointSize(fs)
            fm = QFontMetrics(f)
            if fm.horizontalAdvance(name) < w - icon.width():
                break
            fs -= 1
        p.setFont(f)
        p.drawText(
            icon.width() + self.margin,
            0,
            w - icon.width(),
            round(icon.height() / 2.0),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            name,
        )

        f.setPointSize(8)
        p.setFont(f)
        p.drawText(
            icon.width() + self.margin,
            round(icon.height() / 2.0),
            round(w * 2.0 / 3 - icon.width()),
            round(icon.height() / 4.0),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            "ID: %d" % data["id"],
        )

        coord = "Lon: %.2f\xb0 Lat: %.2f\xb0" % (data["lon"], data["lat"])
        fs = 8
        while True:
            f.setPointSize(fs)
            fm = QFontMetrics(f)
            if fm.horizontalAdvance(coord) < w * 2.0 / 3 - icon.width():
                break
            fs -= 1
        p.setFont(f)
        p.drawText(
            icon.width() + self.margin,
            round(icon.height() * 3 / 4),
            round(w * 2.0 / 3 - icon.width()),
            round(icon.height() / 4.0),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            coord,
        )

        f.setPointSize(12)
        p.setFont(f)
        p.drawText(
            round(w * 2.0 / 3),
            round(icon.height() / 2.0),
            round(w / 3.0),
            round(icon.height() / 2.0),
            Qt.AlignmentFlag.AlignCenter,
            Modes.reverse_mapping[self.i.mode],
        )
        p.translate(0, icon.height() + self.lineh / 2 + self.margin)

    def drawWeather(self, p):
        syslog.syslog(syslog.LOG_DEBUG, "DEBUG  weather_splash drawWeather")
        data = self.i.data
        w = self.w - 2 * self.margin
        h = self.h - 2 * self.margin
        p.setFont(self.font)
        detailed = "detailed"
        if not "detailed" in data and "detailed_0" in data:
            detailed = "detailed_0"
        else:
            syslog.syslog(syslog.LOG_DEBUG, "INFO   drawWeather no detailed info")
        self.drawItem(p, w / 2, "Status:", "%s" % data[detailed])
        if "temp" in data:
            self.drawItem(p, w / 2, "Temperature:", "%.1f \xb0C" % data["temp"])
        else:
            self.drawItem(p, w / 2, "Temperature:", "%.1f \xb0C" % data["temp_day"])
        self.drawItem(
            p,
            w / 2,
            "Temperature (min - max):",
            "%.1f \xb0C - %.1f \xb0C" % (data["temp_min"], data["temp_max"]),
        )
        self.drawItem(p, w / 2, "Coverage:", "%.1f %%" % data["clouds_all"])
        if "wind_speed" in data:
            self.drawItem(
                p,
                w / 2,
                "Wind:",
                "%.1f m/s, %d\xb0" % (data["wind_speed"], data["wind_deg"]),
            )
        self.drawItem(p, w / 2, "Humidity:", "%.1f %%" % data["humidity"])
        self.drawItem(p, w / 2, "Pressure:", "%d mbar" % data["pressure"])
        if "rain_3h" in data:
            self.drawItem(p, w / 2, "Rain (last 3h):", "%d mm" % data["rain_3h"])
        elif "rain_all" in data:
            self.drawItem(p, w / 2, "Rain:", "%d mm" % data["rain_all"])
        else:
            p.translate(0, self.lineh + self.margin)
        if data["sunrise"]:
            self.drawItem(p, w / 2, "Sunrise:", "%s" % time.ctime(data["sunrise"]))
        if data["sunset"]:
            self.drawItem(p, w / 2, "Sunset:", "%s" % time.ctime(data["sunset"]))
        self.drawItem(p, w / 2, "Last updated:", "%s" % time.ctime(data["time"]))
        p.end()
