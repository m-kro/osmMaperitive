SET mypath=%~dp0
SET scriptpath=%mypath%render.script 

REM break if Maperitive not in PATH
where /q maperitive || Maperitive not found. && EXIT /B

REM execute
maperitive -exitafter %scriptpath%