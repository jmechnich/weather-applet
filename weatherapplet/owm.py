import json, syslog, urllib, urllib2

class OWMParser:
    def __init__(self,apikey=None):
        self.args = { 'units': 'metric' }
        if apikey: self.args['apikey'] = apikey
        self.baseurl = 'http://api.openweathermap.org/data/2.5'
    
    def getForecastByName(self, name):
        return self.getWeatherByName( name, 'forecast')

    def getForecastByID(self, locid):
        return self.getWeatherByID( locid, 'forecast')

    def getForecastByCoord(self, lon, lat):
        return self.getWeatherByCoord( lon, lat, 'forecast')

    def getDailyForecastByName(self, name):
        return self.getWeatherByName( name, 'forecast/daily')

    def getDailyForecastByID(self, locid):
        return self.getWeatherByID( locid, 'forecast/daily')

    def getDailyForecastByCoord(self, lon, lat):
        return self.getWeatherByCoord( lon, lat, 'forecast/daily')

    def getWeatherByName(self, name, keyword='weather'):
        args = { 'q': name}
        args.update( self.args)
        url = '%s/%s?' % (self.baseurl,keyword)
        return self.getWeather( url, args)

    def getWeatherByID(self, locid, keyword='weather'):
        args = { 'id': locid}
        args.update( self.args)
        url = '%s/%s?' % (self.baseurl,keyword)
        return self.getWeather( url, args)

    def getWeatherByCoord(self, lon, lat, keyword='weather'):
        args = { 'lon': lon,
                 'lat': lat,
        }
        args.update( self.args)
        url = '%s/%s?' % (self.baseurl,keyword)
        return self.getWeather( url, args)

    def getWeather(self, url, args):
        data = {}
        syslog.syslog( syslog.LOG_DEBUG, "DEBUG  %s" % url+urllib.urlencode(args))
        f = self.connect( url+urllib.urlencode(args))
        if not f:
            return data
        
        j = json.load(f)
        if int(j['cod']) != 200:
            print "Error:", j
            return ret
        
        if j.has_key('city'):
            data.update(self.parseLocation( j['city']))
        if j.has_key('list'):
            data['forecasts'] = []
            for li in j['list']:
                data['forecasts'] += [self.parseWeather(li)]
        if not len(data):
            data.update( self.parseLocation(j))
            data.update( self.parseWeather(j))
        
        return data
            
    def findClosestID( self, lon, lat):
        args = { 'lon': lon,
                 'lat': lat,
        }
        args.update( self.args)
        url = '%s/%s?' % (self.baseurl,'find')

        ret = -1
        f = self.connect( url+urllib.urlencode(args))
        if not f:
            return ret
        
        j = json.load(f)
        if int(j['cod']) != 200:
            print "Error:", j
            return ret
        
        if not j.has_key('list'):
            return ret

        mindist = 1000
        for li in j['list']:
            if not (li.has_key('id') and li.has_key('coord')):
                continue
            tmp_lon = li['coord']['lon']
            tmp_lat = li['coord']['lat']
            dist = pow(lon-tmp_lon,2) + pow(lat-tmp_lat,2)
            if dist < mindist:
                mindist = dist
                ret = li['id']

        return ret

    def getNameFromID( self, locid):
        ret = None
        data = getWeatherByID( locid)
        if len(data) and data.has_key('name'): 
            ret = date['name']
            if data.has_key('country'):
                ret += ", " + data['country']
        return ret

    def parseLocation( self, l):
        d = {}
        for k, v in l.items():
            if k == 'coord':
                d['lon'] = v['lon']
                d['lat'] = v['lat']
            elif k in ['country', 'id', 'name', 'population', 'base']:
                d[k] = v
            elif k == 'sys':
                for k2,v2 in v.items():
                    d[k2] = v2
            # else:
            #     print 2*' ' +k, v
        return d

    def parseWeather( self, w):
        d = {}
        for k, v in w.items():
            if k in [ 'wind', 'rain', 'clouds', 'temp']:
                if type(v) == type(dict()):
                    for key,val in v.items():
                        d['%s_%s' % (k,key)] = val
                else:
                    d['%s_all' % k] = v
            elif k == 'weather':
                if len(v) == 1:
                    li = v[0]
                    d['status']    = li['main']
                    d['weatherid'] = li['id']
                    d['icon']      = li['icon']
                    d['detailed']  = li['description']
                else:
                    count = 0
                    for li in v:
                        d['status_%d' % count]    = li['main']
                        d['weatherid_%d' % count] = li['id']
                        d['icon_%d' % count]      = li['icon']
                        d['detailed_%d' % count]  = li['description']
                        count +=1
            elif k == 'main':
                d['temp']       = v['temp']
                d['temp_min']   = v['temp_min']
                d['temp_max']   = v['temp_max']
                d['temp_kf']    = v.get('temp_kf',0)
                d['humidity']   = v['humidity']
                d['pressure']   = v['pressure']
                d['sea_level']  = v.get('sea_level', -1)
                d['grnd_level'] = v.get('grnd_level', -1)
            elif k == 'sys' and len(v) == 1:
                pass
            elif k == 'dt':
                d['time'] = v
            elif k == 'dt_txt':
                pass
            elif k in ['humidity', 'pressure']:
                d[k] = v
            elif k in ['speed', 'deg']:
                d['wind_'+k] = v
            # else:
            #     print 2*' ' + k, v
        return d
    
    def printData(self, data):
        for k,v in data.items():
            if k == 'forecasts': continue
            print k.ljust(20), v
        print
        for li in data.get('forecasts', []):
            for k,v in li.items():
                print k.ljust(20), v
            print

    def connect(self, url):
        data = None
        retries = 3
        for i in xrange(retries):
            try:
                data = urllib2.urlopen( url)
                break
            except Exception, e:
                syslog.syslog( syslog.LOG_DEBUG,
                               "DEBUG  owm connect error: %s" % str(e))
                syslog.syslog( syslog.LOG_WARNING,
                               "WARN   connection retry %d/%d" % (i+1,retries))
                time.sleep(1)
        else:
            syslog.syslog( syslog.LOG_ERR,
                           "ERROR  failed to retrieve data from '%s'" % url)
        return data

