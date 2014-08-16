from appletlib.splash import Splash

from utils import Location, Modes

import time, syslog

from PyQt4.Qt import *

class SplashWeather(Splash):
    def __init__(self,indicator):
        Splash.__init__(self)
        self.i = indicator
        self.initVars()
        self.updateSplash()
    
    def initVars(self):
        self.margin = 2
        self.width  = 200
        self.height = 250
        self.lineh  = 15
        
    def updateSplash(self):
        self.fitContents()
        self.update()
    
    def fitContents(self):
        if not self.i.data or not len(self.i.data):
            self.width  = 150
            self.height = self.lineh
        else:
            items = 12
            self.width  = 300
            self.height = 50+(self.lineh+self.margin)*items
        self.resize( self.width, self.height)

    def wheelEvent(self,ev):
        ev.accept()
        if ev.delta() < 0 and self.i.mode < Modes.N-1:
            self.i.mode += 1
            self.i.updateActions()
            self.updateSplash()
        elif ev.delta() > 0 and self.i.mode > 0:
            self.i.mode -= 1
            self.i.updateActions()
            self.updateSplash()
        
    def paintEvent(self,ev):
        ev.accept()
        self.fitContents()
        p = QPainter(self)
        p.setFont( self.font)
        p.fillRect( self.rect(), self.i.s.bgColor)
        p.setPen(self.i.s.fgColor)
        p.translate(self.margin,self.margin)
        data = self.i.data
        if not data or not len(data):
            p.drawText( 0, 0, self.width, self.height,
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
        for i in xrange(0,5):
            hour = '%s%d' % (prefix,i)
            if not self.i.data.has_key(hour): break
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
        for i in xrange(0,5):
            day = 'daily%d' % i
            if not self.i.data.has_key(day): break
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
        w=self.width-2*self.margin
        h=self.height-2*self.margin
        
        icon = QPixmap(self.i.iconPath(data['icon']))
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
        w=self.width-2*self.margin
        h=self.height-2*self.margin
        p.setFont( self.font)
        self.drawItem(p, w/2, u'Status:', u'%s' % data['detailed'])
        if data.has_key('temp'):
            self.drawItem(p, w/2, u'Temperature:',
                          u'%.1f \xb0C' % data['temp'])
        else:
            self.drawItem(p, w/2, u'Temperature:',
                          u'%.1f \xb0C' % data['temp_day'])
        self.drawItem(p, w/2, u'Temperature (min - max):',
                      u'%.1f \xb0C - %.1f \xb0C' % 
                      (data['temp_min'], data['temp_max']))
        self.drawItem(p, w/2, u'Coverage:', u'%.1f %%' % data['clouds_all'])
        if data.has_key('wind_speed'):
            self.drawItem(p, w/2, u'Wind:', u'%.1f m/s, %d\xb0' %
                          (data['wind_speed'],data['wind_deg']))
        self.drawItem(p, w/2, u'Humidity:', u'%.1f %%' % data['humidity'])
        self.drawItem(p, w/2, u'Pressure:', u'%d mbar' % data['pressure'])
        if data.has_key('rain_3h'):
            self.drawItem(p, w/2, u'Rain (last 3h):', u'%d mm' % data['rain_3h'])
        elif data.has_key('rain_all'):
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
