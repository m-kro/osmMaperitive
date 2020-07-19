# Ausgabe: [Name] [Länge, gerundet auf 5m und in m]
def paddleLabel(e):
    roundBy = 5
    val = ''
    for set in e.tagSets:
        if set.hasTag('length') and set.hasTag('name'):
            return "%s %.0f m" % (set['name'], round(float(set['length'])/roundBy,0)*roundBy)
    return ''
