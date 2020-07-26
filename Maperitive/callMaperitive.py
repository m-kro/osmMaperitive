import os, sys
import subprocess
from shutil import which
from xml.etree import ElementTree as etree



def findElements(root, elTag, elFilter):
    result = {}
    for el in root.findall(elTag):
        accepted = False
        for tagEl in el.findall('tag'):
            for key, val in elFilter.items():
                if tagEl.attrib['k'] == key and tagEl.attrib['v'] == val:
                    accepted = True
                    break
            if accepted:
                break
        if accepted:
            attDict = {}
            for tagEl in el.findall('tag'):
                attDict[tagEl.attrib['k']] = tagEl.attrib['v']
            if elTag == 'way':
                nodeEls = el.findall('nd')
                if len(nodeEls) > 0:
                    attDict['firstNodeRef'] = nodeEls[0].attrib['ref']
                    attDict['lastNodeRef'] = nodeEls[-1].attrib['ref']         
            result[el.attrib['id']] = attDict
            pass
    return result 

def connectElements(ways, points):
    for wayID, way in ways.items():
        if not 'length' in way:
            continue        
        if 'firstNodeRef' in way and way['firstNodeRef'] in points:
            nodeID = way['firstNodeRef']
            if 'edgeSet' not in points[nodeID]:
                points[nodeID]['edgeSet'] = set()
            points[nodeID]['edgeSet'].add(wayID)
        if 'lastNodeRef' in way and way['lastNodeRef'] in points:
            nodeID = way['lastNodeRef']
            if 'edgeSet' not in points[nodeID]:
                points[nodeID]['edgeSet'] = set()
            points[nodeID]['edgeSet'].add(wayID)
                    

scriptDir = os.path.dirname(os.path.realpath(__file__))

# check dependencies
neededApps = ['inkscape', 'maperitive']
for neededApp in neededApps:
    if which(neededApp) is None:
        sys.exit("%s is crucial but cannot be accessed." % neededApp)

# call Maperitive and wait until it finishes
scriptPath = os.path.join(scriptDir, 'render.script')
process = subprocess.Popen(['maperitive', '-exitafter', scriptPath])
process.wait()

# call Inkscape for SVG to PDF conversion
svgFiles = ['BS_Okerumflut.svg', 'BS_Nord.svg', 'BS_Sued.svg']
resultDir = os.path.dirname(os.path.dirname(scriptPath))
for svgFile in svgFiles:
    svgPath = os.path.join(resultDir , "Result", svgFile)
    pdfPath = os.path.abspath("%s.pdf" % os.path.splitext(svgPath)[0])
    print("Convert to %s." % pdfPath)
    process = subprocess.Popen(['inkscape', svgPath, '--without-gui', '--export-area-page', '--export-pdf-version=1.4', "--export-pdf=%s" % pdfPath])
    process.wait()        

print("Finishes printing maps.")

# collect interesting items: way[waterway=river], node[note=Abschnitt]
tree = etree.parse(os.path.join(os.path.dirname(scriptDir), 'OSM', 'WFBSGF.osm'))
root = tree.getroot()
pointFilter = {'note': 'Abschnitt'}
wayFilter = {'waterway': 'river'}
ways = findElements(root, 'way', wayFilter)
points = findElements(root, 'node', pointFilter)
connectElements(ways, points)

# find branching points / start points: either 1 or 3+ connected edges
for pointID, point in points.items():
    if 'edgeSet' in point:
        edgeCount = len(point['edgeSet'])
        if edgeCount == 1 or edgeCount > 2:
            print("%s (%s) is a branching point" % (pointID, point['name'] if 'name' in point else ''))
            







