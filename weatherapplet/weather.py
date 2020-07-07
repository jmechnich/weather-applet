from appletlib.indicator      import Indicator
from appletlib.app            import Application

from weatherapplet.owm            import OWMParser
from weatherapplet.utils          import Location, Modes, OWMError
from weatherapplet.prefs          import Preferences
from weatherapplet.weather_splash import SplashWeather

import json, os, syslog, time, urllib.request
from datetime import datetime, timedelta

from PyQt5.Qt import *

class WeatherIndicator(Indicator):
    # update every hour
    update_interval = 60*60*1000
    reasonDict = dict((v,k) for k,v in  QSystemTrayIcon.__dict__.items())
    
    def __init__(self):
        super(WeatherIndicator,self).__init__('weather', self.update_interval)
        self.func = self.updateAll
        self.initVars()
        self.initOwm()
        self.initContextMenu()
        self.initStats()
        self.initWidgets()
        qApp.sigusr1.connect(self.restart)

    def initVars(self):
        self.data         = {}
        self.mode_actions = {}
        self.mode         = int(Application.settingsValue('mode',
                                                     Modes.Now))
        self.location     = int(Application.settingsValue('location',
                                                     Location.Auto))
        self.locid        = int(Application.settingsValue('locid', '-1'))
        self.apikey       = str(Application.settingsValue('apikey', ''))
        self.cachedir     = os.path.join( os.environ['HOME'], '.cache',
                                          str(qApp.applicationName()))
        self.prefs        = None
        self.icon         = None
        self.locvalid     = False if self.locid == -1 else True
        
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
        m.addAction(QIcon.fromTheme("view-refresh"), "&Update",
                    self.updateAll)
        m.addAction(QIcon.fromTheme("preferences-other"), "&Options",
                    self.showPreferences)
        m.addAction(QIcon.fromTheme("application-exit"), "&Quit", qApp.quit)
        self.systray.setContextMenu(m)
        
    def initStats(self):
        self.systray.triggerUpdate.connect( self.func)
        self.systray.triggerWheel.connect( self.cycleMode)
        self.systray.activated.connect( self.systrayClicked)

    def initWidgets(self):
        self.splash = SplashWeather(self)
        self.prefs  = Preferences(self)
        self.updateAll()

    def setAPIKey(self, apikey):
        self.apikey = apikey
        Application.setSettingsValue('apikey', self.apikey)
        self.owm.setAPIKey(self.apikey)
        if not self.locvalid:
            if not self.setLocationFromIP():
                return
            self.updateLocation()
            self.prefs.initContents()

    def setLocation(self,l):
        self.location = l
        Application.setSettingsValue('location', self.location)

    def setLocationFromIP(self):
        syslog.syslog( syslog.LOG_DEBUG, "DEBUG  weather setLocationFromIP")
        lon=0
        lat=0
        try:
            src = "https://freegeoip.app/json/"
            f = urllib.request.urlopen(src)
            j = json.load(f)
            lon = j.get( 'longitude')
            lat = j.get( 'latitude')
        except Exception as e:
            syslog.syslog(
                syslog.LOG_ERR,
                "ERROR  weather setLocationFromIP failed: %s" % str(e))

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
        if not 'id' in data: return False
        self.locid = data['id']
        self.locvalid = True
        syslog.syslog( syslog.LOG_DEBUG,
                       "DEBUG  weather setLocationFromName: %d" % self.locid)
        return True

    def setLocationFromCoord(self, lon, lat):
        syslog.syslog( syslog.LOG_DEBUG,
                       "DEBUG  weather setLocationFromCoord %f %f" % (lon,lat))
        if lon in self.data and lat in self.data:
            if self.data['lon'] == lon and self.data['lat'] == lat:
                syslog.syslog(
                    syslog.LOG_DEBUG,
                    "DEBUG   data already up to date")
                return False
        locid = self.owm.findClosestID(lon, lat)
        if locid == -1:
            syslog.syslog(syslog.LOG_DEBUG,
                          "DEBUG   error finding closest OWM ID")
            return False
        if self.locid == locid and len(self.data): return False
        self.locid = locid
        self.locvalid = True
        syslog.syslog( syslog.LOG_DEBUG,
                       "DEBUG  weather setLocationFromCoord: %d" % self.locid)
        return True
    
    def updateLocation(self):
        syslog.syslog( syslog.LOG_DEBUG, "DEBUG  weather updateLocation")
        self.updateAll()
        if self.location != Location.Auto and \
           self.locid    != -1 and \
           self.locvalid == True:
            Application.setSettingsValue('locid', self.locid)
        
    def showPreferences(self):
        self.prefs.show()
        
    def setMode(self, m):
        syslog.syslog( syslog.LOG_DEBUG, "DEBUG  weather setMode %d" % m)
        self.mode = m
        Application.setSettingsValue( 'mode', m)
        if self.splash:
            syslog.syslog( syslog.LOG_DEBUG,
                           "DEBUG  weather setMode updateSplash")
            self.updateSplashGeometry()
            self.splash.updateSplash()
            self.splash.show()
    
    def cycleMode(self, delta):
        if delta < 0 and self.mode < Modes.N-1:
            self.mode += 1
            self.updateActions()
            if self.splash: self.splash.updateSplash()
        elif delta > 0 and self.mode > 0:
            self.mode -= 1
            self.updateActions()
            if self.splash: self.splash.updateSplash()
        
    def systrayClicked(self,reason):
        syslog.syslog( syslog.LOG_DEBUG, "DEBUG  weather systrayClicked '%s'" %\
                       self.reasonDict[reason])
        if reason == QSystemTrayIcon.Trigger or \
                reason == QSystemTrayIcon.DoubleClick:
            if not self.splash: return
            if self.splash.isVisible():
                self.splash.hide()
            else:
                self.updateSplashGeometry(hide=True)
                self.splash.show()
        elif reason == QSystemTrayIcon.MiddleClick:
            self.restart()
        elif reason == QSystemTrayIcon.Context:
            pass
        elif reason == QSystemTrayIcon.Unknown:
            print("unknown")

    def restart(self):
        self.reset()
        self.initContextMenu()
        self.initStats()
        self.updateIcon()
        self.prefs.group_loc.button(self.location).setChecked(True)
        
    def iconPath(self,icon):
        trgdir = os.path.join( self.cachedir, 'icons')
        trg = os.path.join( trgdir, '%s.png' % icon)
        if not os.path.exists(trgdir):
            os.makedirs( trgdir)
        if not os.path.exists( trg):
            src = "http://openweathermap.org/img/w/%s.png" % icon
            f = urllib.request.urlopen(src)
            output = open( trg, 'wb')
            output.write(f.read())
            output.close()
        return trg
        
    def updateActions(self):
        Application.setSettingsValue('mode', self.mode)
        self.mode_actions[self.mode].setChecked(True)
    
    def updateAll(self):
        syslog.syslog( syslog.LOG_INFO, "INFO   updateAll at %s" %
                       datetime.now().isoformat())
        self.data.clear()
        try:
            self.updateWeather()
            self.updateForecast()
            self.updateDailyForecast()
        except OWMError as e:
            syslog.syslog( syslog.LOG_ERR, "ERR  weather %s" % e)
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
            if not self.locvalid:
                self.locid = -1
            return
        
        self.data.update(data)
        self.locvalid = True

    def updateForecast(self):
        syslog.syslog( syslog.LOG_DEBUG, "DEBUG  weather updateForecast")
        if self.locid == -1:
            syslog.syslog( syslog.LOG_DEBUG,
                           "DEBUG  weather locid is empty")
            return

        data = self.owm.getForecastByID( self.locid)
        
        if not len(data):
            syslog.syslog( syslog.LOG_WARNING,
                           "WARN  could not get forecast for '%d'" % self.locid)
            if not self.locvalid:
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
                           "WARN  could not get daily forecast for '%d'" % self.locid)
            if not self.locvalid:
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
        pix.fill( self.systray.bgColor)
        p = QPainter(pix)
        f = QFont("Dejavu Sans", 6)
        p.setFont( f)
        p.setPen(self.systray.fgColor)
        if not len(self.data):
            syslog.syslog( syslog.LOG_ERR, "ERR     updateIcon no data")
            p.drawText( 0, 0, pix.width(), pix.height(), Qt.AlignCenter, "ERR")
            p.end()
            self.systray.setIcon( QIcon(pix))
            if self.splash: self.splash.updateSplash()
            return
        iconname = 'icon'
        if iconname in self.data:
            pass
        elif 'icon_0' in self.data:
            iconname = 'icon_0'
        else:
            syslog.syslog( syslog.LOG_WARNING, "WARN  updateIcon no icon")
            p.drawText( 0, 0, pix.width(), pix.height(), Qt.AlignCenter, "ERR")
            p.end()
            self.systray.setIcon( QIcon(pix))
            if self.splash: self.splash.updateSplash()
            return
        bg = QPixmap( self.iconPath(self.data[iconname]))
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
        self.systray.setIcon(self.icon)
        if self.prefs: self.prefs.setWindowIcon(self.icon)

    def locationName(self):
        ret = ''
        if 'name' in self.data:
            ret = self.data['name']
            if 'country' in self.data:
                ret += ', ' + self.data['country']
        return ret

    def locationCoord(self):
        ret = ''
        if 'lon' in self.data and 'lat' in self.data:
            ret = '%f,%f' % (self.data['lon'],self.data['lat'])
        return ret
