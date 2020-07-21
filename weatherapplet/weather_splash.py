from appletlib.splash import Splash

from weatherapplet.utils import Location, Modes

import time, syslog

from PyQt5.Qt import *

class SplashWeather(Splash):
    def __init__(self,indicator):
        super(SplashWeather,self).__init__()
        self.i = indicator
        self.initVars()
        self.updateSplash()
    
    def initVars(self):
        self.margin = 2
        self.w      = 200
        self.h      = 250
        self.lineh  = 15
        
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
            self.h = 50+(self.lineh+self.margin)*items
        self.resize(self.w, self.h)

    def wheelEvent(self,ev):
        ev.accept()
        self.i.cycleMode(ev.angleDelta().y())
        
    def paintEvent(self,ev):
        ev.accept()
        self.fitContents()
        p = QPainter(self)
        p.setFont( self.font)
        p.fillRect( self.rect(), self.i.systray.bgColor)
        p.setPen(self.i.systray.fgColor)
        p.translate(self.margin,self.margin)
        data = self.i.data
        if not data or not len(data):
            p.drawText( 0, 0, self.w, self.h,
                        Qt.AlignCenter, "No data available")
            p.end()
            return
        self.drawHeader(p)
        if self.i.mode == Modes.Now:
            self.drawWeather(p)
        elif self.i.mode == Modes.Today:
            self.drawDay(p)
        elif self.i.mode == Modes.Tomorrow:
            self.drawDay(p,prefix='tomorrow')
        elif self.i.mode == Modes.Week:
            self.drawWeek(p)
            

    def drawDay(self, p, prefix='today'):
        syslog.syslog( syslog.LOG_DEBUG, "DEBUG  weather_splash drawDay")
        p.save()
        iconoff = 50
        hdrw = 45
        y = iconoff+self.margin
        p.setFont( self.font)
        p.drawText( 0, y, hdrw, self.lineh, Qt.AlignCenter, "Time")
        y += self.lineh + self.margin
        p.drawText( 0, y, hdrw, self.lineh, Qt.AlignCenter, "Status")
        y += self.lineh + self.margin
        y += self.lineh + self.margin
        p.drawText( 0, y, hdrw, self.lineh, Qt.AlignCenter, "Temp")
        y += self.lineh + self.margin
        p.drawText( 0, y, hdrw, self.lineh, Qt.AlignCenter, "Min")
        y += self.lineh + self.margin
        p.drawText( 0, y, hdrw, self.lineh, Qt.AlignCenter, "Max")
        y += self.lineh + self.margin
        p.drawText( 0, y, hdrw, self.lineh, Qt.AlignCenter, "Wind")
        y += self.lineh + self.margin
        p.drawText( 0, y, hdrw, self.lineh, Qt.AlignCenter, "Rain/3h")
        p.translate(hdrw,0)
        for i in range(5):
            hour = '%s%d' % (prefix,i)
            if not hour in self.i.data: break
            data = self.i.data[hour]
            icon = QPixmap(self.i.iconPath(data['icon']))
            y = 0
            p.drawPixmap(0, y, icon.width(), icon.height(), icon)
            y += icon.height() + self.margin
            p.drawText( 0, y, icon.width(), self.lineh,
                        Qt.AlignCenter, "%s" %
                        time.strftime("%H:%M", time.localtime(data['time'])))
            y += self.lineh + self.margin
            p.drawText( 0, y, icon.width(), self.lineh,
                        Qt.AlignCenter, "%s" % data['status'])
            y += self.lineh + self.margin
            y += self.lineh + self.margin
            p.drawText( 0, y, icon.width(), self.lineh,
                        Qt.AlignVCenter | Qt.AlignRight,
                        "%.1f \xb0C" % data['temp'])
            y += self.lineh + self.margin
            p.drawText( 0, y, icon.width(), self.lineh,
                        Qt.AlignVCenter | Qt.AlignRight,
                        "%.1f \xb0C" % data['temp_min'])
            y += self.lineh + self.margin
            p.drawText( 0, y, icon.width(), self.lineh,
                        Qt.AlignVCenter | Qt.AlignRight,
                        "%.1f \xb0C" % data['temp_max'])
            y += self.lineh + self.margin
            p.drawText( 0, y, icon.width(), self.lineh,
                        Qt.AlignVCenter | Qt.AlignRight,
                        "%.1f m/s" % data.get('wind_speed', 0))
            y += self.lineh + self.margin
            p.drawText( 0, y, icon.width(), self.lineh,
                        Qt.AlignVCenter | Qt.AlignRight,
                        "%d mm" % data.get('rain_3h', 0))
            p.translate(icon.width(),0)
        p.restore()
            
    def drawWeek(self,p):
        syslog.syslog( syslog.LOG_DEBUG, "DEBUG  weather_splash drawWeek")
        p.save()
        iconoff = 50
        hdrw = 45
        y = iconoff+self.margin
        p.setFont( self.font)
        y += self.lineh + self.margin
        p.drawText( 0, y, hdrw, self.lineh, Qt.AlignCenter, "Date")
        y += self.lineh + self.margin
        p.drawText( 0, y, hdrw, self.lineh, Qt.AlignCenter, "Status")
        y += self.lineh + self.margin
        y += self.lineh + self.margin
        p.drawText( 0, y, hdrw, self.lineh, Qt.AlignCenter, "Morning")
        y += self.lineh + self.margin
        p.drawText( 0, y, hdrw, self.lineh, Qt.AlignCenter, "Day")
        y += self.lineh + self.margin
        p.drawText( 0, y, hdrw, self.lineh, Qt.AlignCenter, "Eve")
        y += self.lineh + self.margin
        p.drawText( 0, y, hdrw, self.lineh, Qt.AlignCenter, "Night")
        p.translate(hdrw,0)
        for i in range(5):
            day = 'daily%d' % i
            if not day in self.i.data: break
            data = self.i.data[day]
            icon = QPixmap(self.i.iconPath(data['icon']))
            y = 0
            p.drawPixmap(0, y, icon.width(), icon.height(), icon)
            y += icon.height()
            p.drawText( 0, y, icon.width(), self.lineh,
                        Qt.AlignCenter, "%s" %
                        time.strftime("%a", time.localtime(data['time'])))
            y += self.lineh + self.margin*2
            p.drawText( 0, y, icon.width(), self.lineh,
                        Qt.AlignCenter, "%s" %
                        time.strftime("%h %d", time.localtime(data['time'])))
            y += self.lineh + self.margin
            p.drawText( 0, y, icon.width(), self.lineh,
                        Qt.AlignCenter, "%s" % data['status'])
            y += self.lineh + self.margin
            y += self.lineh + self.margin
            p.drawText( 0, y, icon.width(), self.lineh,
                        Qt.AlignVCenter | Qt.AlignRight,
                        "%.1f \xb0C" % data['temp_morn'])
            y += self.lineh + self.margin
            p.drawText( 0, y, icon.width(), self.lineh,
                        Qt.AlignVCenter | Qt.AlignRight,
                        "%.1f \xb0C" % data['temp_day'])
            y += self.lineh + self.margin
            p.drawText( 0, y, icon.width(), self.lineh,
                        Qt.AlignVCenter | Qt.AlignRight,
                        "%.1f \xb0C" % data['temp_eve'])
            y += self.lineh + self.margin
            p.drawText( 0, y, icon.width(), self.lineh,
                        Qt.AlignVCenter | Qt.AlignRight,
                        "%.1f \xb0C" % data['temp_night'])
            p.translate(icon.width(),0)
        p.restore()
    
    def drawItem(self, p, center, title, value):
        p.drawText( 0, 0, center, self.lineh, Qt.AlignLeft | Qt.AlignVCenter,
                    title)
        p.drawText( center, 0, center, self.lineh,
                    Qt.AlignLeft | Qt.AlignVCenter,
                    value)
        p.translate(0,self.lineh+self.margin)
    
    def drawHeader(self, p):
        syslog.syslog( syslog.LOG_DEBUG, "DEBUG  weather_splash drawHeader")
        data = self.i.data
        w=self.w-2*self.margin
        h=self.h-2*self.margin

        iconname = 'icon'
        if iconname in data:
            pass
        elif 'icon_0' in data:
            iconname = 'icon_0'
        else:
            syslog.syslog( syslog.LOG_WARNING, "WARN  drawHeader no icon")
            syslog.syslog( syslog.LOG_DEBUG, repr(data.keys()))
        icon = QPixmap(self.i.iconPath(data[iconname]))
        p.drawPixmap(0, 0, icon.width(), icon.height(), icon)

        name = data['name']
        if len(data['country']):
            name += ', '+ data['country']
        f = QFont(self.font)
        fs = 12
        while True:
            f.setPointSize(fs)
            fm = QFontMetrics(f)
            if fm.width(name) < w-icon.width():
                break
            fs -= 1
        p.setFont(f)
        p.drawText( icon.width()+self.margin, 0,
                    w-icon.width(), icon.height()/2.,
                    Qt.AlignLeft | Qt.AlignVCenter,
                    name)

        f.setPointSize(8)
        p.setFont(f)
        p.drawText( icon.width()+self.margin, icon.height()/2.,
                    w*2./3-icon.width(), icon.height()/4.,
                    Qt.AlignLeft | Qt.AlignVCenter,
                    "ID: %d" % data['id'])

        coord = u"Lon: %.2f\xb0 Lat: %.2f\xb0" % (data['lon'], data['lat'])
        fs = 8
        while True:
            f.setPointSize( fs)
            fm = QFontMetrics(f)
            if fm.width(coord) < w*2./3-icon.width():
                break
            fs -= 1
        p.setFont(f)
        p.drawText( icon.width()+self.margin, icon.height()*3/4,
                    w*2./3-icon.width(), icon.height()/4.,
                    Qt.AlignLeft | Qt.AlignVCenter,
                    coord)
        
        f.setPointSize(12)
        p.setFont(f)
        p.drawText( w*2./3, icon.height()/2.,
                    w/3., icon.height()/2.,
                    Qt.AlignCenter,
                    Modes.reverse_mapping[self.i.mode])
        p.translate(0,icon.height()+self.lineh/2+self.margin)
        
    def drawWeather(self, p):
        syslog.syslog( syslog.LOG_DEBUG, "DEBUG  weather_splash drawWeather")
        data = self.i.data
        w=self.w-2*self.margin
        h=self.h-2*self.margin
        p.setFont( self.font)
        detailed = 'detailed'
        if not 'detailed' in data and 'detailed_0' in data:
            detailed = 'detailed_0'
        else:
            syslog.syslog( syslog.LOG_DEBUG,
                           "INFO   drawWeather no detailed info")
        self.drawItem(p, w/2, u'Status:', u'%s' % data[detailed])
        if 'temp' in data:
            self.drawItem(p, w/2, u'Temperature:',
                          u'%.1f \xb0C' % data['temp'])
        else:
            self.drawItem(p, w/2, u'Temperature:',
                          u'%.1f \xb0C' % data['temp_day'])
        self.drawItem(p, w/2, u'Temperature (min - max):',
                      u'%.1f \xb0C - %.1f \xb0C' % 
                      (data['temp_min'], data['temp_max']))
        self.drawItem(p, w/2, u'Coverage:', u'%.1f %%' % data['clouds_all'])
        if 'wind_speed' in data:
            self.drawItem(p, w/2, u'Wind:', u'%.1f m/s, %d\xb0' %
                          (data['wind_speed'],data['wind_deg']))
        self.drawItem(p, w/2, u'Humidity:', u'%.1f %%' % data['humidity'])
        self.drawItem(p, w/2, u'Pressure:', u'%d mbar' % data['pressure'])
        if 'rain_3h' in data:
            self.drawItem(p, w/2, u'Rain (last 3h):',
                          u'%d mm' % data['rain_3h'])
        elif 'rain_all' in data:
            self.drawItem(p, w/2, u'Rain:', u'%d mm' % data['rain_all'])
        else:
            p.translate(0,self.lineh+self.margin)
        if data['sunrise']:
            self.drawItem(p, w/2, u'Sunrise:',
                          u'%s' % time.ctime(data['sunrise']))
        if data['sunset']:
            self.drawItem(p, w/2, u'Sunset:',
                          u'%s' % time.ctime(data['sunset']))
        self.drawItem(p, w/2, u'Last updated:',
                      u'%s' % time.ctime(data['time']))
        p.end()
