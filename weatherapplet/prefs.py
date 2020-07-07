from weatherapplet.utils import Location, Modes

import syslog

from PyQt5.Qt import *

class Preferences(QDialog):
    def __init__(self, indicator):
        super(Preferences,self).__init__()
        self.i = indicator
        self.location = {}
        self.mapping = dict(zip(Location.reverse_mapping.keys(),[
            self.setLocationFromIP,
            self.setLocationFromName,
            self.setLocationFromCoord,
            self.setLocationFromID,
            self.setLocationFromPreset,
        ]))
        self.layout = QVBoxLayout()
        self.init()
        self.setLayout(self.layout)
        if self.i.icon:
            self.setWindowIcon( self.i.icon)
        
    def init(self):
        g = QGroupBox("General")
        v = QGridLayout()

        v.addWidget(QLabel("OWM API key"), 0, 0)
        self.apikey = QLineEdit(self.i.apikey)
        self.apikey.returnPressed.connect(
            lambda: self.i.setAPIKey(self.apikey.text()))
        v.addWidget(self.apikey, 0, 1)

        g.setLayout(v)
        self.layout.addWidget(g)

        g = QGroupBox("Location")
        v = QGridLayout()
        self.group_loc = QButtonGroup()

        tmp = QRadioButton("Automatically (from IP)")
        self.group_loc.addButton(tmp, Location.Auto)
        v.addWidget( tmp, 0, 0, 1, 2)

        tmp = QRadioButton("From name:")
        self.group_loc.addButton(tmp, Location.Name)
        v.addWidget( tmp, 1, 0)
        tmp = QLineEdit( self.i.locationName())
        self.location[Location.Name] = tmp
        tmp.returnPressed.connect( self.setLocationFromName)
        v.addWidget( tmp, 1, 1)

        tmp = QRadioButton("From coordinates:")
        self.group_loc.addButton(tmp, Location.Coord)
        v.addWidget( tmp, 2, 0)
        tmp = QLineEdit(self.i.locationCoord())
        coord_val = QRegExpValidator( QRegExp("[\d\.]+\s*,\s*[\d\.]+"), self)
        tmp.setValidator( coord_val)
        self.location[Location.Coord] = tmp
        tmp.returnPressed.connect( self.setLocationFromCoord)
        v.addWidget( tmp, 2, 1)
        
        tmp = QRadioButton("From OWM ID:")
        self.group_loc.addButton(tmp, Location.ID)
        v.addWidget( tmp, 3, 0)
        tmp = QLineEdit(str(self.i.locid))
        tmp.setValidator( QIntValidator())
        self.location[Location.ID] = tmp
        tmp.returnPressed.connect( self.setLocationFromID)
        v.addWidget( tmp, 3, 1)

        # disabled for now
        #tmp = QRadioButton("From Preset:")
        #self.group_loc.addButton(tmp, Location.Preset)
        #v.addWidget( tmp, 4, 0)
        #tmp = QPushButton()
        #self.location[Location.Preset] = tmp
        #tmp.clicked.connect( self.setLocationFromPreset)
        #v.addWidget( tmp, 4, 1)

        g.setLayout(v)
        self.layout.addWidget(g)
        
        self.group_loc.buttonClicked.connect(self.selectLocation)
        sb = self.group_loc.button(self.i.location)
        sb.setChecked(True)
        self.selectLocation(sb)

    def initContents(self):
        self.apikey.setText(self.i.apikey)
        self.location[Location.Name].setText(self.i.locationName())
        self.location[Location.Coord].setText(self.i.locationCoord())
        self.location[Location.ID].setText(str(self.i.locid))
        self.group_loc.button(self.i.location).setChecked(True)

    def showEvent(self, ev):
        self.initContents()
        
    def selectLocation(self,b):
        selected = self.group_loc.id(b)
        syslog.syslog( syslog.LOG_DEBUG,
                       "DEBUG  prefs selectLocation %d" % selected)
        for k,v in self.location.items():
            v.setEnabled(False)
        if selected in self.location:
            self.location[selected].setEnabled(True)
        self.i.setLocation(selected)
        self.mapping[selected]()
    
    def setLocationFromIP(self):
        syslog.syslog( syslog.LOG_DEBUG, "DEBUG  prefs setLocationFromIP")
        if not self.i.setLocationFromIP(): return
        self.i.updateLocation()
        self.location[Location.Name].setText(self.i.locationName())
        self.location[Location.Coord].setText(self.i.locationCoord())
        self.location[Location.ID].setText(str(self.i.locid))

    def setLocationFromName(self):
        syslog.syslog( syslog.LOG_DEBUG, "DEBUG  prefs setLocationFromName")
        if not self.i.setLocationFromName(
                str(self.location[Location.Name].text())):
            return
        self.i.updateLocation()
        self.location[Location.Name].setText(self.i.locationName())
        self.location[Location.Coord].setText(self.i.locationCoord())
        self.location[Location.ID].setText(str(self.i.locid))
        
    def setLocationFromCoord(self):
        syslog.syslog( syslog.LOG_DEBUG, "DEBUG  prefs setLocationFromCoord")
        l = str(self.location[Location.Coord].text()).split(',')
        if len(l) != 2: return

        if not self.i.setLocationFromCoord( float(l[0]), float(l[1])): return
        self.i.updateLocation()
        self.location[Location.Name].setText(self.i.locationName())
        self.location[Location.Coord].setText(self.i.locationCoord())
        self.location[Location.ID].setText(str(self.i.locid))
    
    def setLocationFromID(self):
        syslog.syslog( syslog.LOG_DEBUG, "DEBUG  prefs setLocationFromID")
        locid = int(self.location[Location.ID].text())
        if locid == self.i.locid: return
        self.i.locid = locid
        self.i.updateLocation()
        self.location[Location.Name].setText(self.i.locationName())
        self.location[Location.Coord].setText(self.i.locationCoord())
        self.location[Location.ID].setText(str(self.i.locid))
        
    def setLocationFromPreset(self):
        syslog.syslog( syslog.LOG_DEBUG, "DEBUG  prefs setLocationFromPreset")
