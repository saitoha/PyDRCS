#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ***** BEGIN LICENSE BLOCK *****
# Copyright (C) 2012-2013  Hayaki Saito <user@zuse.jp>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# ***** END LICENSE BLOCK *****

__author__  = "Hayaki Saito (user@zuse.jp)"
__version__ = "0.0.2"
__license__ = "GPL v3"

import os, sys, optparse, select
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

from drcs import *

def _printver():
        print '''
drcsconv %s
Copyright (C) 2012-2013 Hayaki Saito <user@zuse.jp>. 

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see http://www.gnu.org/licenses/.
        ''' % __version__

def main():

    parser = optparse.OptionParser()
    
    parser.add_option("-8", "--8bit-mode",
                      default=False,
                      action="store_true",
                      dest="f8bit",
                      help="Generate a drcs font image for 8bit terminal or printer")
   
    parser.add_option("-7", "--7bit-mode",
                      action="store_false",
                      dest="f8bit",
                      help="Generate a drcs font image for 7bit terminal or printer")
 
    parser.add_option("-n", "--negate",
                      action="store_true",
                      dest="negate",
                      default=False,
                      help="Negate image")

    parser.add_option("-u", "--unicode",
                      action="store_true",
                      dest="uni",
                      default=False,
                      help="Use drcsterm's DRCS-unicode mapping")
 
    parser.add_option("-c", "--columns",
                      dest="columns",
                      default="62",
                      help="Image width in cell size (default=62, max=62)")

    parser.add_option("-r", "--rows",
                      dest="rows",
                      help="Image height in cell size")
     
    parser.add_option('--version', dest='version',
                      action="store_true", default=False,
                      help='show version')
   
    options, args = parser.parse_args()

    if options.version:
        _printver()
        return

    writer = DrcsWriter(f8bit=options.f8bit)

    if select.select([sys.stdin, ], [], [], 0.0)[0]:
        imagefile = StringIO(sys.stdin.read())
    elif len(args) == 0 or args[0] == '-':
        imagefile = StringIO(sys.stdin.read())
    else:
        imagefile = args[0]

    columns = int(options.columns)
    if columns > 62:
        print "Wrong columns value is specified (max: 62)."
        return
     
    rows = options.rows
    if not rows is None:
        rows = int(rows)

    writer.draw(imagefile, columns, rows, options.negate, options.uni)

if __name__ == '__main__':
    main()

