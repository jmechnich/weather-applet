def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = dict((value, key) for key, value in enums.items())
    enums['reverse_mapping'] = reverse
    enums['N'] = len(sequential)
    return type('Enum', (), enums)

Modes    = enum( 'Now', 'Today', 'Tomorrow', 'Week')
Location = enum( 'Auto', 'Name', 'Coord', "ID", "Preset")

class OWMError(Exception):
    def __init__(self,msg):
        self.msg = msg
    def __str__(self):
        return self.msg
