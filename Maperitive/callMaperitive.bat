SET mypath=%~dp0
SET scriptpath=%mypath%render.script 

REM break if Maperitive or Inkscape are not in PATH
where /q maperitive || Maperitive not found. && EXIT /B
where /q inkscape || Inkscape not found. && EXIT /B

REM execute
maperitive -exitafter %scriptpath%

REM export svg to pdf
inkscape ../Result/BS_Okerumflut.svg --without-gui --export-area-page --export-pdf-version=1.4 --export-pdf=../Result/BS_okerumflut.pdf
