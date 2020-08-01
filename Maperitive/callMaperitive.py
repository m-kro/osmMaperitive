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
            attDict['id'] = el.attrib['id']       
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
neededApps = ['inkscape', 'maperitive', 'pdflatex']
for neededApp in neededApps:
    if which(neededApp) is None:
        sys.exit("%s is crucial but cannot be accessed." % neededApp)

# call Maperitive and wait until it finishes
scriptPath = os.path.join(scriptDir, 'render.script')
process = subprocess.Popen(['maperitive', '-exitafter', scriptPath])
process.wait()

# call Inkscape for SVG to PDF conversion
svgFiles = ['WF.svg', 'BS_Sued.svg', 'BS_Sued2.svg', 'BS_Okerumflut.svg', 'BS_Nord.svg', 'BS_Nord2.svg', 'GF.svg']
resultDir = os.path.join(os.path.dirname(os.path.dirname(scriptPath)), 'Result')
for svgFile in svgFiles:
    svgPath = os.path.join(resultDir , svgFile)
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
branchPointIDs = []
for pointID, point in points.items():
    if 'edgeSet' in point:
        edgeCount = len(point['edgeSet'])
        if edgeCount > 2:
            branchPointIDs.append(pointID)
        if edgeCount == 1 or edgeCount > 2:
            print("%s (%s) is an end or branching point" % (pointID, point['name'] if 'name' in point else ''))
            
# accumulate distance between branchPoints and other targets
cumulativeDists = {}
for branchPointID in branchPointIDs:
    startPoint = points[branchPointID]
    startName = startPoint['name'] if 'name' in startPoint else branchPointID
    visited = []
    cumulativeDists[branchPointID] = []
    
    for edgeID in startPoint['edgeSet']:
        distances = []
        currentEdgeID = edgeID
        if currentEdgeID not in visited:
            currentPoint = startPoint
            cumulDist = 0.0
            while True:
                endPointID = ways[currentEdgeID]['lastNodeRef'] if currentPoint['id'] == ways[currentEdgeID]['firstNodeRef'] else ways[currentEdgeID]['firstNodeRef']
                cumulDist += float(ways[currentEdgeID]['length'])
                distances.append((branchPointID, endPointID, cumulDist))
                if 'edgeSet' not in points[endPointID]:
                    print("missing edgeSet for point on edge %s" % ways[edgeID]['name'])
                    exit(-1)                
                if len(points[endPointID]['edgeSet']) != 2:
                    break
                else:
                    currentPoint = points[endPointID]
                    for eID in points[endPointID]['edgeSet']:
                        if eID != currentEdgeID:
                            currentEdgeID = eID
                            break     
                visited.append(currentEdgeID)
            print("Start edge %s" % edgeID)
        cumulativeDists[branchPointID].append(distances)
        
        for relStart, relEnd, dist in distances:
            print("%s (%s) > %s (%s): %.0f m" % (relStart, points[relStart]['name'] if 'name' in points[relStart] else '', relEnd, points[relEnd]['name'] if 'name' in points[relEnd] else '', dist))    

# print rounded distances to PDF / latex
# write to csv
csvPath = os.path.join(scriptDir, "distances.csv")
sep = ';'
roundBy = 5
with open(csvPath, 'w', encoding='utf-8') as csvFile:
    csvFile.write("%s\n" % sep.join(['Von', 'Nach', 'Entfernung [m]']))
    for branchPointID, distanceList in cumulativeDists.items():
        for distances in distanceList:
            firstDataLine = True
            for dataset in distances:
                roundedDist = "%.0f" % (round(dataset[2]/roundBy,0)*roundBy)
                endName = points[dataset[1]]['name'] if 'name' in points[dataset[1]] else dataset[1]
                if firstDataLine:
                    startName = points[dataset[0]]['name'] if 'name' in points[dataset[0]] else dataset[0]
                    
                    csvFile.write("%s\n" % sep.join([startName, endName, roundedDist]))
                    firstDataLine = False
                else:
                    csvFile.write("%s\n" % sep.join(['', endName, roundedDist]))



# call pdflatex to generate the result PDF
os.chdir(scriptDir)
texPath = os.path.join(scriptDir, 'distTable.tex')
process = subprocess.Popen(['pdflatex', '-output-directory', resultDir, texPath])
process.wait()   
