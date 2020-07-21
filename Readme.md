# Custom paddling map rendering in Maperitive

This repository contains a trial of how to render a paddling map from OpenStreetMap data. It contains river sections labeled with 
their lengths, allowing paddlers to plan their daily training tour and log the distance traveled.

## System setup

The base OpenStreetMap file has been enhanced to provide the necessary information with the help of [JOSM](https://josm.openstreetmap.de) editor:
- The existing river ways have been split/joined to span from one landmark/bridge/branch to the next.
- Length as calculated by JOSM has been added to the ways'tags
- The ways have been named adequately
- Start/end nodes of the river ways where tagged with note=Abschnitt

Map rendering is done with Maperitive, a map renderer available for free at [maperitive.net](http:///maperitive.net). 
Maperitive executable needs to be in Windows PATH env. variable to use the batch map script.
- A python script concatenates name and rounded length information of the ways
- A new rule set draws the river sections with the labels and end nodes
- The map can be saved as vector image, e.g. PDF

A SVG image can be created by calling Maperitive/callMaperitive.bat.

## Feedback
If you have ideas how this should evolve please let me know.