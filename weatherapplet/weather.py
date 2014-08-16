from appletlib.indicator      import Indicator
from appletlib.app            import Application

from owm            import OWMParser
from utils          import Location, Modes
from prefs          import Preferences
from weather_splash import SplashWeather

import json, os, syslog, time, urllib2
from datetime import datetime, timedelta

from PyQt4.Qt import *

class WeatherIndicator(Indicator):
    def __init__(self):
        Indicator.__init__(self, 'weather', 60*60*1000)
        self.func = self.updateAll
        self.initVars()
        self.initOwm()
        self.initContextMenu()
        self.initStats()
        self.initWidgets()

    def initVars(self):
        self.data         = {}
        self.mode_actions = {}
        self.mode         = int(Application.settingsValue('mode',
                                                     Modes.Now).toInt()[0])
        self.location     = int(Application.settingsValue('location',
                                                     Location.Auto).toInt()[0])
        self.locid        = str(Application.settingsValue('locid',
                                                     '-1').toString())
        self.apikey       = str(Application.settingsValue('apikey', '').toString())
        self.cachedir     = os.path.join( os.environ['HOME'], '.cache',
                                          str(qApp.applicationName()))
        self.prefs        = None
        self.icon         = None
        
    def initOwm(self):
        self.owm = OWMParser(self.apikey if len(self.apikey) else None)
    
    def initContextMenu(self):
        m = QMenu()
        g = QActionGroup(m)
        g.setExclusive(True)
        sm = QSignalMapper(m)
        for i in range(0,Modes.N):
            name = Modes.reverse_mapping[i]
            a = g.addAction( name)
            a.setCheckable(True)
            if self.mode == i:
                a.setChecked( True)
            m.addAction(a)
            a.triggered.connect( sm.map)
            sm.setMapping( a, i)
            self.mode_actions[i] = a
        sm.mapped.connect( self.setMode)
        m.addSeparator()
        m.addAction( QIcon.fromTheme("options"), "&Options",
                     self.showPreferences)
        m.addAction( QIcon.fromTheme("application-exit"), "&Quit", qApp.quit)
        self.s.setContextMenu(m)
        
    def initStats(self):
        self.s.triggerUpdate.connect( self.func)
        self.s.activated.connect( self.systrayClicked)

    def initWidgets(self):
        self.splash = SplashWeather(self)
        self.updateAll()
        self.prefs  = Preferences(self)

    def setLocation(self,l):
        self.location = l
        Application.setSettingsValue('location', self.location)

    def setLocationFromIP(self):
        syslog.syslog( syslog.LOG_DEBUG, "DEBUG  weather setLocationFromIP")
        lon=0
        lat=0
        try:
            src = "http://freegeoip.net/json/"
            f = urllib2.urlopen(src)
            j = json.load(f)
            lon = j.get( 'longitude')
            lat = j.get( 'latitude')
        except:
            return False
        syslog.syslog( syslog.LOG_DEBUG,
                       "DEBUG  weather setLocationFromIP %f %f" %
                       (lon,lat))
        
        return self.setLocationFromCoord(lon,lat)
    
    def setLocationFromName(self, s):
        syslog.syslog( syslog.LOG_DEBUG,
                       "DEBUG  weather setLocationFromName %s" % s)
        if self.locationName().startswith( s): return False
        data = self.owm.getWeatherByName(s)
        if not len(data): return False
        if not data.has_key('id'): return False
        self.locid = data['id']
        syslog.syslog( syslog.LOG_DEBUG,
                       "DEBUG  weather setLocationFromName: %d" % self.locid)
        return True

    def setLocationFromCoord(self, lon, lat):
        syslog.syslog( syslog.LOG_DEBUG,
                       "DEBUG  weather setLocationFromCoord %f %f" % (lon,lat))
        if self.data.has_key(lon) and self.data.has_key(lat):
            if self.data['lon'] == lon and self.data['lat'] == lat:
                return False
        locid = self.owm.findClosestID(lon, lat)
        if locid == -1: return False
        if self.locid == locid and len(self.data): return False
        self.locid = locid
        syslog.syslog( syslog.LOG_DEBUG,
                       "DEBUG  weather setLocationFromCoord: %d" % self.locid)
        return True
    
    def updateLocation(self):
        syslog.syslog( syslog.LOG_DEBUG, "DEBUG  weather updateLocation")
        self.updateAll()
        if self.location != Location.Auto and (self.locid != -1):
            Application.setSettingsValue('locid', self.locid)
        
    def showPreferences(self):
        self.prefs.show()
        
    def setMode( self, m):
        syslog.syslog( syslog.LOG_DEBUG, "DEBUG  weather setMode %d" % m)
        self.mode = m
        Application.setSettingsValue( 'mode', m)
        if self.splash:
            self.updateSplashGeometry()
            self.splash.updateSplash()
            self.splash.show()
        
    def systrayClicked(self,reason):
        syslog.syslog( syslog.LOG_DEBUG,
                       "DEBUG  weather systrayClicked %d" % reason)
        if reason == QSystemTrayIcon.Trigger or \
                reason == QSystemTrayIcon.DoubleClick:
            if not self.splash: return
            if self.splash.isVisible():
                self.splash.hide()
            else:
                self.updateSplashGeometry(hide=True)
                self.splash.show()
        elif reason == QSystemTrayIcon.MiddleClick:
            self.reset()
            self.initContextMenu()
            self.initStats()
            self.updateIcon()
            self.prefs.group_loc.button(self.location).setChecked(True)
        elif reason == QSystemTrayIcon.Context:
            pass
        elif reason == QSystemTrayIcon.Unknown:
            print "unknown"

    def iconPath(self,icon):
        trgdir = os.path.join( self.cachedir, 'icons')
        trg = os.path.join( trgdir, '%s.png' % icon)
        if not os.path.exists(trgdir):
            os.makedirs( trgdir)
        if not os.path.exists( trg):
            src = "http://openweathermap.org/img/w/%s.png" % icon
            f = urllib2.urlopen(src)
            output = open( trg, 'wb')
            output.write(f.read())
            output.close()
        return trg
        
    def updateActions(self):
        Application.setSettingsValue('mode', self.mode)
        self.mode_actions[self.mode].setChecked(True)
    
    def updateAll(self):
        syslog.syslog( syslog.LOG_INFO, "INFO   updateAll")
        self.data.clear()
        self.updateWeather()
        self.updateForecast()
        self.updateDailyForecast()
        self.updateIcon()
        if self.splash:
            self.splash.updateSplash()
        syslog.syslog( syslog.LOG_DEBUG, "DEBUG  weather updateAll end")
    
    def updateWeather(self):
        syslog.syslog( syslog.LOG_DEBUG, "DEBUG  weather updateWeather")
        if self.locid == -1:
            syslog.syslog( syslog.LOG_DEBUG, "DEBUG  weather locid is empty")
            return
        
        data = self.owm.getWeatherByID( self.locid)
        if not len(data):
            syslog.syslog( syslog.LOG_WARNING,
                           "WARN  could not get weather for '%d'" % self.locid)
            self.locid = -1
            return
        
        self.data.update(data)

    def updateForecast(self):
        syslog.syslog( syslog.LOG_DEBUG, "DEBUG  weather updateForecast")
        if self.locid == -1:
            syslog.syslog( syslog.LOG_DEBUG,
                           "DEBUG  weather locid is empty")
            return

        data = self.owm.getForecastByID( self.locid)
        
        if not len(data):
            syslog.syslog( syslog.LOG_WARNING,
                           "WARN  could not get weather for '%d'" % self.locid)
            self.locid = -1
            return

        today = datetime.today()
        tomorrow = (datetime.today()+timedelta(days=1)).replace(hour=7)
        c1 = 0
        c2 = 0
        for forecast in data.get('forecasts', []):
            d = datetime.fromtimestamp(forecast['time'])
            if d > today:
                self.data['today%d' % c1] = forecast
                c1 += 1
            if d > tomorrow:
                self.data['tomorrow%d' % c2] = forecast
                c2 += 1
 
    def updateDailyForecast(self):
        syslog.syslog( syslog.LOG_DEBUG, "DEBUG  weather updateDailyForecast")
        if self.locid == -1:
            syslog.syslog( syslog.LOG_DEBUG,
                           "DEBUG  weather locid is empty")
            return

        data = self.owm.getDailyForecastByID( self.locid)

        if not len(data):
            syslog.syslog( syslog.LOG_WARNING,
                           "WARN  could not get weather for '%d'" % self.locid)
            self.locid = -1
            return

        # try filling five days starting from start (defaults to tomorrow)
        today = datetime.today()
        count = 0
        for forecast in data.get('forecasts', []):
            d = datetime.fromtimestamp(forecast['time'])
            if d > today:
                self.data['daily%d' % count] = forecast
                count += 1
        
    def updateIcon(self):
        syslog.syslog( syslog.LOG_DEBUG, "DEBUG  weather updateIcon")

        pix = QPixmap(22, 22)
        pix.fill( self.s.bgColor)
        p = QPainter(pix)
        f = QFont("Dejavu Sans", 6)
        p.setFont( f)
        p.setPen(self.s.fgColor)
        if not len(self.data):
            syslog.syslog( syslog.LOG_DEBUG, "INFO  updateIcon no data")
            p.drawText( 0, 0, pix.width(), pix.height(), Qt.AlignCenter, "ERR")
            p.end()
            self.s.setIcon( QIcon(pix))
            if self.splash: self.splash.updateSplash()
            return
        bg = QPixmap( self.iconPath(self.data['icon']))
        sx = float(pix.width())/bg.width()
        sy = float(pix.height())/bg.height()
        p.save()
        p.translate( pix.width()/2, pix.height()/2)
        p.scale( sx, sy)
        p.translate( -pix.width()/2/sx, -(pix.height()/2+5)/sy)
        p.drawPixmap( 0, 0, bg)
        p.restore()
        p.drawText( pix.rect(), Qt.AlignBottom|Qt.AlignHCenter,
                    u"%d\xb0C" % round(self.data['temp']))
        p.end()
        self.icon = QIcon(pix)
        self.s.setIcon(self.icon)
        if self.prefs: self.prefs.setWindowIcon(self.icon)

    def locationName(self):
        ret = ''
        if self.data.has_key('name'):
            ret = self.data['name']
            if self.data.has_key('country'):
                ret += ', ' + self.data['country']
        return ret

    def locationCoord(self):
        ret = ''
        if self.data.has_key('lon') and self.data.has_key('lat'):
            ret = '%f,%f' % (self.data['lon'],self.data['lat'])
        return ret