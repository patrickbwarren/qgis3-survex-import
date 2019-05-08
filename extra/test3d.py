#!/usr/bin/env python2.7

# Emulate dump3d in python (assuming v8 of .3d format)

# Based on library to handle Survex 3D files (*.3d) 
# Copyright (C) 2008-2012 Thomas Holder, http://sf.net/users/speleo3/

# Modifications copyright (c) 2018-2019 Patrick B Warren

# Distributed under the terms of the GNU General Public License v2

import argparse
from struct import unpack
from datetime import date
import math as m

styles = {0x00 : 'NORMAL',
          0x01 : 'DIVING',
          0x02 : 'CARTESIAN',
          0x03 : 'CYLPOLAR',
          0x04 : 'NOSURVEY'}

line_flags = {0x01 : 'SURFACE',
              0x02 : 'DUPLICATE',
              0x04 : 'SPLAY'}

node_flags = {0x01 : 'SURFACE',
              0x02 : 'UNDERGROUND',
              0x04 : 'ENTRANCE',
              0x08 : 'EXPORTED',
              0x10 : 'FIXED',
              0x20 : 'ANON'}

day_zero = date(1900, 1, 1).toordinal()

def to_date(days):
    """Convert from integer days since 1990.01.01 to a string YYYY.mm.dd"""
    return date.fromordinal(day_zero + days).strftime('%Y.%m.%d')

def to_date_range(days1, days2):
    """Convert from integer days range to a string YYYY.mm.dd-YYYY.mm.dd"""
    return to_date(days1) + '-' + to_date(days2)

def to_string(ijk):
    """Convert xyz, lrud, nlehv (error info) tuples to strings"""
    if len(ijk) == 3:
        x, y, z = ijk
        return '%0.2f %0.2f %0.2f' % (0.01*x, 0.01*y, 0.01*z)
    if len(ijk) == 4:
        l, r, u, d = ijk
        return '%0.2f %0.2f %0.2f %0.2f' % (0.01*l, 0.01*r, 0.01*u, 0.01*d)
    if len(ijk) == 5:
        n, l, e, h, v = ijk
        return '#legs %i, len %0.2fm, E %0.2f H %0.2f V %0.2f' % (n, 0.01*l, 0.01*e, 0.01*h, 0.01*v)

def to_lrud_string(lrud, label, date_string):
    """Convert LRUD data to string and annotate with label and date"""
    s = '%s [%s]' % (to_string(lrud), label)
    if args.show_dates and date_string:
        s = s + ' ' + date_string
    return s

def read_xyz(fp):
    """Read xyz as signed integers according to .3d spec and return as tuple""" 
    return unpack('<iii', fp.read(12))
        
def read_len(fp):
    """Read a number as a length according to .3d spec"""
    byte = ord(fp.read(1))
    if byte != 0xff:
        return byte
    else:
        return unpack('<I', fp.read(4))[0]

def read_label(fp, current_label):
    """Read a string as a label, or part thereof, according to .3d spec"""
    byte = ord(fp.read(1))
    if byte != 0x00:
        ndel = byte >> 4
        nadd = byte & 0x0f
    else:
        ndel = read_len(fp)
        nadd = read_len(fp)
    oldlen = len(current_label)
    return current_label[:oldlen - ndel] + fp.read(nadd).decode('ascii')

# Command line arguments

parser = argparse.ArgumentParser(description='Dump contents of .3d file to stdout')
parser.add_argument('-d', '--show-dates', action='store_true', help='show survey date information (if present)')
parser.add_argument('FILE')
args = parser.parse_args()
    
# Start reading file

with open(args.FILE, 'rb') as fp:
    
    line = fp.readline().rstrip() # File ID
    if not line.startswith(b'Survex 3D Image File'):
        raise IOError('Not a Survex 3D File: ' + args.FILE)

    line = fp.readline().rstrip() # File format version
    if not line.startswith(b'v'):
        raise IOError('Unrecognised .3d version: ' + args.FILE)
    version = int(line[1:])
    if version < 8:
        raise IOError('Version >= 8 required: ' + args.FILE)

    line = fp.readline().rstrip() # Metadata (title and coordinate system)
    title, cs = [s.decode('utf-8') for s in line.split(b'\x00')]

    line = fp.readline().rstrip() # Timestamp
    if not line.startswith(b'@'):
        raise IOError('Unrecognised timestamp: ' + args.FILE)
    timestamp = int(line[1:])

    # Write file header to match output of dump3d
    
    print('TITLE "%s"' % title)
    print('DATE "@%i"' % timestamp)
    print('DATE_NUMERIC %i' % timestamp)
    print('CS %s' % cs)
    print('VERSION %i' % version)
    print("SEPARATOR '.'")
    print('--')

    # System-wide flags

    flag = ord(fp.read(1))

    if flag & 0x80:
        raise IOError('Flagged as extended elevation: ' + args.FILE)

    # All front-end data read in, now read byte-wise according to .3d spec, and process
    
    current_label = ''
    current_date = None
    current_style = 0xff

    traverse_list = []
    traverse_label = []
    current_traverse = []

    xsect_list = []
    current_xsect = []

    station_xyz = {}

    while True:

        char = fp.read(1)

        if not char: # End of file reached (prematurely?)
            raise IOError('Premature end of file: ' + args.FILE)

        byte = ord(char)

        if byte <= 0x05: # STYLE
            if byte == 0x00 and current_style == 0x00: # this signals end of data
                print('STOP')
                if current_traverse:
                    traverse_list.append(current_traverse)
                    traverse_label.append(current_label)
                break # escape from byte-gobbling while loop
            else:
                current_style = byte
                
        elif byte <= 0x0e: # Reserved
            continue
        
        elif byte == 0x0f: # MOVE
            xyz = read_xyz(fp)
            print('MOVE ' + to_string(xyz))
            if current_traverse:
                traverse_list.append(current_traverse)
                traverse_label.append(current_label)
                current_traverse = []
            current_traverse.append(xyz)

        elif byte == 0x10: # DATE (none)
            current_date = None
            
        elif byte == 0x11: # DATE (single date)
            days = unpack('<H', fp.read(2))[0]
            current_date = to_date(days)
            
        elif byte == 0x12:  # DATE (date range, short format)
            days, extra = unpack('<HB', fp.read(3))
            current_date = to_date_range(days, days + extra + 1)

        elif byte == 0x13: # DATE (date range, long format)
            days1, days2 = unpack('<HH', fp.read(4))
            current_date = to_date_range(days1, days2)

        elif byte <= 0x1e: # Reserved
            continue
        
        elif byte == 0x1f:  # Error info
            nlehv = unpack('<iiiii', fp.read(20))
            print('ERROR_INFO ' + to_string(nlehv))
            
        elif byte <= 0x2f: # Reserved
            continue
        
        elif byte <= 0x33: # XSECT
            current_label = read_label(fp, current_label)
            if byte & 0x02: # short or long format
                lrud = unpack('<iiii', fp.read(16))
            else:
                lrud = unpack('<hhhh', fp.read(8))
            print('XSECT ' + to_lrud_string(lrud, current_label, current_date))
            current_xsect.append((current_label, lrud))
            if byte & 0x01:
                print('XSECT_END')
                xsect_list.append(current_xsect)
                current_xsect = []
            
        elif byte <= 0x3f: # Reserved
            continue
        
        elif byte <= 0x7f: # LINE
            flag = byte & 0x3f
            if not (flag & 0x20):
                current_label = read_label(fp, current_label)
            xyz = read_xyz(fp)
            flags = [v for k, v in sorted(line_flags.iteritems()) if flag & k]
            tag = styles[current_style]
            if flags:
                tag = tag + ' ' + ' '.join(flags)
            if args.show_dates and current_date:
                tag = tag + ' ' + current_date
            print('LINE %s [%s] STYLE=%s' % (to_string(xyz), current_label, tag))
            current_traverse.append(xyz)

        elif byte <= 0xff: # LABEL (or NODE)
            flag = byte & 0x7f
            current_label = read_label(fp, current_label)
            xyz = read_xyz(fp)
            flags = [v for k, v in sorted(node_flags.iteritems()) if flag & k]
            if flags:
                tag = ' '.join(flags)
                print('NODE %s [%s] %s' % (to_string(xyz), current_label, tag))
            else:
                print('NODE %s [%s]' % (to_string(xyz), current_label))
            station_xyz[current_label] = xyz

# file closes automatically, with open(args.FILE, 'rb') as fp:

#with open('traverses.dat', 'w') as fp:
#    for i, traverse in enumerate(traverse_list):
#        print traverse_label[i], traverse
#        for xyz in traverse:
#            fp.write('%0.2f\t%0.2f\t%s\n' % (0.01*xyz[0], 0.01*xyz[1], traverse_label[i]))
#        fp.write('&\n')

xoff, yoff = traverse_list[0][0][0:2]
        
with open('stations.dat', 'w') as fp:
    for label in station_xyz:
#        print label, station_xyz[label]
        xyz = station_xyz[label]
        fp.write("%0.2f\t%0.2f\n" % (0.01*(xyz[0]-xoff), 0.01*(xyz[1]-yoff)))


with open('centers.dat', 'w') as fcenters:
    with open('xsects.dat', 'w') as fxsect:
        with open('walls.dat', 'w') as fwalls:
            with open('quads.dat', 'w') as fquads:
    
                for xsect in xsect_list:

                    if len(xsect) < 2:
                        continue

                    data = []
                    for label, lrud in xsect:
                        xyz = station_xyz[label]
                        data.append(xyz + lrud[0:2])

                    for x, y, z, l, r in data:
                        fcenters.write("%0.2f\t%0.2f\n" % (0.01*(x-xoff), 0.01*(y-yoff)))
                    fcenters.write('&\n')

                    dirn = []
                    for i, (x, y, z, l, r) in enumerate(data):
                        if i > 0:
                            dx, dy, dz = x - xp, y - yp, z - zp
                            dh2 = dx*dx + dy*dy
                            norm = m.sqrt(dh2 + dz*dz)
                            dx, dy = (-dy/norm, dx/norm) if norm > 0 and dh2 > 0 else (0, 0)
                            dirn.append((dx, dy))
                        xp, yp, zp = x, y, z

                    left_wall = []
                    right_wall = []
        
                    for i, (x, y, z, l, r) in enumerate(data):
                        d1x, d1y = dirn[i-1] if i > 0 else (0, 0)
                        d2x, d2y = dirn[i] if i+1 < len(data) else (0, 0)
                        dx, dy = d1x+d2x, d1y+d2y
                        norm = m.sqrt(dx*dx + dy*dy)
                        ex, ey = (dx/norm, dy/norm) if norm > 0 else (0, 0)
                        left_wall.append((x+l*ex, y+l*ey, z))
                        right_wall.append((x-r*ex, y-r*ey, z))
                        
                    for x, y, z in left_wall:
                        fwalls.write("%0.2f\t%0.2f\n" % (0.01*(x-xoff), 0.01*(y-yoff)))
                    fwalls.write('&\n')

                    for x, y, z in right_wall:
                        fwalls.write("%0.2f\t%0.2f\n" % (0.01*(x-xoff), 0.01*(y-yoff)))
                    fwalls.write('&\n')

                    for (x1, y1, z1), (x2, y2, z2) in zip(left_wall, right_wall):
                        fxsect.write("%0.2f\t%0.2f\n" % (0.01*(x1-xoff), 0.01*(y1-yoff)))
                        fxsect.write("%0.2f\t%0.2f\n" % (0.01*(x2-xoff), 0.01*(y2-yoff)))
                        fxsect.write('&\n')

                    for i, xyz_pair in enumerate(zip(left_wall, right_wall)):
                        if i > 0:
                            quad = tuple(reversed(prev_xyz_pair)) + xyz_pair + (prev_xyz_pair[1],)
                            for i, p in enumerate(quad):
                                x, y = p[0:2]
                                fquads.write("%0.2f\t%0.2f\n" % (0.01*(x-xoff), 0.01*(y-yoff)))
                            fquads.write('&\n')
                        prev_xyz_pair = xyz_pair

                            

                            
