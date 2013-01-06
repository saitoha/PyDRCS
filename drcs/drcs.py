#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
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


import sys, os, termios, select
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

class DrcsConverter:

    def __init__(self, image, f8bit, columns, rows=None, negate=False, uni=False):

        import Image
        if f8bit: # 8bit mode
            self.DCS='\x90'
            self.ST='\x9c'
        else:
            self.DCS='\x1bP'
            self.ST='\x1b\\'

        self.cellwidth = 15
        self.cellheight = 24
        self.columns = columns
        width, height = image.size
        if rows is None:
            rows = int(1.0 * columns * height / width / self.cellheight * self.cellwidth )
        self.rows = rows
        self.negate = negate
        self.uni = uni
        width = self.cellwidth * self.columns
        height = self.cellheight * rows
        image = image.resize((width, height))
        image = image.convert("L")
        image = image.convert("1")
        self.palette = image.getpalette()
        self.data = image.getdata()

    def __write_header(self, output, fbyte):

        # start Device Control String (DCS)
        output.write(self.DCS)

        # write header
        cellwidth = self.cellwidth
        cellheight = self.cellheight
        output.write('1;0;0;%d;1;2;%d;0{ %c' % (cellwidth, cellheight, fbyte))

    def __write_body_section(self, output, n):

        data = self.data

        #write body section
        cellheight = self.cellheight
        cellwidth = self.cellwidth
        width = self.cellwidth * self.columns
        startpos = width * cellheight * n
        positive = 255 if self.negate else 0
        for c in xrange(0, self.columns):
            startx = cellwidth * c
            for y in xrange(0, cellheight, 6):
                if y != 0:
                    output.write("/")
                for x in range(0, cellwidth):
                    acc = 0
                    for i in xrange(0, 6):
                        acc = acc * 2
                        index = (y + 5 - i) * width + startx + x
                        if data[startpos + index] == positive:
                            acc += 1
                    output.write(chr(acc + 0x3f))
            output.write(";")

    def __write_terminator(self, output):
        # write ST
        output.write(self.ST) # terminate Device Control String

    def getvalue(self):

        if self.uni:
            import codecs
            output = codecs.getwriter("utf-8")(StringIO())
        else:
            output = StringIO()

        try:
            for n in xrange(0, self.rows):
                self.__write_header(output, 0x40 + n)
                self.__write_body_section(output, n)
                self.__write_terminator(output)

            output.write("\n")

            if self.uni:
                for dscs in xrange(0, self.rows):
                    for c in xrange(0, self.columns):
                        code = 0x100000 | 0x40 + dscs << 8 | 0x21 + c
                        code -= 0x10000
                        c1 = (code >> 10) + 0xd800
                        c2 = (code & 0x3ff) + 0xdc00
                        output.write(unichr(c1) + unichr(c2))
                    output.write("\n")

            else:
                for dscs in xrange(0, self.rows):
                    output.write("\x1b( %c" % (0x40 + dscs))
                    for c in xrange(0, self.columns):
                        output.write(chr(0x21 + c))
                    output.write("\x1b(B\n")

            value = output.getvalue()

        finally:
            output.close()

        return value

class DrcsWriter:

    def __init__(self, f8bit = False):
        self.f8bit = f8bit
        if f8bit: # 8bit mode
            self.CSI='\x9b'
        else:
            self.CSI='\x1b['

    def draw(self, filename, columns=62, rows=None, negate=False, uni=False):
        import Image # PIL
        image = Image.open(filename)
        drcs_converter = DrcsConverter(image, self.f8bit, columns, rows, negate, uni)
        sys.stdout.write(drcs_converter.getvalue())

