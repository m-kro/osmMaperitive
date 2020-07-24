import os, sys
import subprocess
from shutil import which


# check dependencies
neededApps = ['inkscape', 'maperitive']
for neededApp in neededApps:
    if which(neededApp) is None:
        sys.exit("%s is crucial but cannot be accessed." % neededApp)

# call Maperitive and wait until it finishes
scriptPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'render.script')
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

# TODO: calculate total lengths of paddle edges