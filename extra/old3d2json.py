#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Original code copyright (c) 2019 Patrick B Warren
# Modifications copyright (c) 2023 Nat Dalton

# Distributed under the terms of the GNU General Public License v2

# usage: ./old3d2json.py [--epsg=EPSG] <filename> sends to stdout

# For example ./old3d2json.py --epsg=31255 1627_65.3d > 1627_65.json

# EPSG:31255 is MGI / Austria GK Central CRS

# Small correction (2023) by Nat Dalton at line 41 in the current file
# adds a check for an empty list of fields.

import sys
import json

# sort out the command line arguments

try:
    if '--epsg' in sys.argv[1]:
        _, epsg = sys.argv[1].split('=', 2)
        filename = sys.argv[2]
    else:
        epsg, filename = None, sys.argv[1]
except IndexError:
    print('Missing file name')
    print('Usage: %s [--epsg=EPSG] <filename>' % sys.argv[0])
    raise SystemExit

# read the file and accumulate lists of legs and stations

line, lines = None, []
names, coords = [], []

with open(filename) as f:
    for record in f:
        fields = record.split()
        if fields: # added empty list check for fields (ND mod)
            if fields[0] in ['move', 'draw', 'name']:
                xyz = [float(v) for v in fields[-3:]] # last three fields
                if fields[0] == 'move':
                    if line: # catch the last line string
                        lines.append(line)
                    line = [xyz] # start a new line string
                elif fields[0] == 'draw':
                    line.append(xyz) # grow the current line string
                elif fields[0] == 'name':
                    if line: # catch the last line string
                        lines.append(line)
                    names.append(fields[1]) # keep the name..
                    coords.append(xyz) # .. and the position

# create a GIS data structure as a hierarchy of dicts and lists

features = []

for i, line in enumerate(lines):
    geometry = {'type': 'LineString'}
    geometry['coordinates'] = line
    feature = {'type': 'Feature'}
    feature['geometry'] = geometry
    feature['properties'] = {'fid': i}
    features.append(feature)

for i, (name, xyz) in enumerate(zip(names, coords)):
    geometry = {'type': 'Point'}
    geometry['coordinates'] = xyz
    feature = {'type': 'Feature'}
    feature['geometry'] = geometry
    feature['properties'] = {'fid': i, 'name': name}
    features.append(feature)    

feature_collection = {'type': 'FeatureCollection'}
feature_collection['features'] = features

# add the CRS as a property of the feature collection

if epsg: 
    crs = {'type': 'name'}
    crs['properties'] = {'name': 'urn:ogc:def:crs:EPSG::%i' % int(epsg)}
    feature_collection['crs'] = crs

# finally write the data structure as a JSON to stdout

print(json.dumps(feature_collection, indent=2))

# END

