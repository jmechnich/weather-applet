def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = dict((value, key) for key, value in enums.iteritems())
    enums['reverse_mapping'] = reverse
    enums['N'] = len(sequential)
    return type('Enum', (), enums)

Modes    = enum( 'Now', 'Today', 'Tomorrow', 'Week')
Location = enum( 'Auto', 'Name', 'Coord', "ID", "Preset")
