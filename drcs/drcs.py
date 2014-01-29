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

import sys
import os

class DrcsConverter:

    def __init__(self, image, f8bit, columns,
                 rows=None, negate=False, use_unicode=False, ncolor=1):
        if f8bit:  # 8bit mode
            self.DCS = '\x90'
            self.ST = '\x9c'
        else:
            self.DCS = '\x1bP'
            self.ST = '\x1b\\'

        self.cellwidth = 15
        self.cellheight = 24
        self.columns = columns
        width, height = image.size
        if rows is None:
            display_width = columns * self.cellwidth
            display_height = 1.0 * display_width * height / width
            rows = int(display_height / self.cellheight)
        self.rows = rows
        self.negate = negate
        self._use_unicode = use_unicode
        width = self.cellwidth * self.columns
        height = self.cellheight * rows
        image = image.resize((width, height))

        if ncolor > 256:
            ncolor = 256
        self._ncolor = ncolor

        if ncolor == 1:
            image = image.convert("L")
            image = image.convert("1")
            self.palette = None
        else:
            from PIL import Image
            image = image.convert("P", palette=Image.ADAPTIVE, colors=ncolor)
            self.palette = image.getpalette()
        self.data = image.getdata()

    def __write_header(self, output, fbyte):

        # start Device Control String (DCS)
        output.write(self.DCS)

        # write header
        cellwidth = self.cellwidth
        cellheight = self.cellheight
        if self._ncolor > 1:
            pt = 3
        else:
            pt = 1
        output.write('1;0;0;%d;1;%d;%d;0{ %c' % (cellwidth, pt, cellheight, fbyte))

    def _write_sixel_palette(self, output):

        palette = self.palette

        # write palette section
        for i in xrange(0, self._ncolor * 3, 3):
            no = i / 3
            r = palette[i + 0] * 100 / 256
            g = palette[i + 1] * 100 / 256
            b = palette[i + 2] * 100 / 256
            output.write('#%d;2;%d;%d;%d' % (no, r, g, b))

    def _write_colored_sixel(self, output, data, width, top, keycolor):

        n = 1
        for y in xrange(top, top + 6):
            p = y * width
            cached_no = data[p]
            count = 1
            c = -1
            for x in xrange(0, width):
                color_no = data[p + x]
                if color_no == cached_no and count < 255:
                    count += 1
                else:
                    if cached_no == keycolor:
                        c = 0x3f
                    else:
                        c = n + 0x3f
                    if count == 1:
                        output.write('#%d%c' % (cached_no, c))
                    elif count == 2:
                        output.write('#%d%c%c' % (cached_no, c, c))
                        count = 1
                    else:
                        output.write('#%d!%d%c' % (cached_no, count, c))
                        count = 1
                    cached_no = color_no
            if c != -1:
                if cached_no == keycolor:
                    c = 0x3f 
                if count == 1:
                    output.write('#%d%c' % (cached_no, c))
                elif count == 2:
                    output.write('#%d%c%c' % (cached_no, c, c))
                else:
                    output.write('#%d!%d%c' % (cached_no, count, c))
            output.write('$')  # write line terminator
            if n == 32:
                n = 1
                output.write('-')  # write sixel line separator
            else:
                n <<= 1


    def __write_body_section(self, output, n):

        data = self.data

        #write body section
        cellheight = self.cellheight
        cellwidth = self.cellwidth
        width = self.cellwidth * self.columns

        if self.palette:
            for y in xrange(cellheight * n, cellheight * (n + 1), 6):
                self._write_colored_sixel(output, data, width, y, -1)
        else:
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
        output.write(self.ST)  # terminate Device Control String

    def write(self, output):

        if self._use_unicode:
            import codecs
            output = codecs.getwriter("utf-8")(output)

        for n in xrange(0, self.rows):
            self.__write_header(output, 0x40 + n)
            if self._ncolor > 1:
                self._write_sixel_palette(output)
            self.__write_body_section(output, n)
            self.__write_terminator(output)

        output.write("\n")

        if self._use_unicode:
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

class DrcsWriter:

    def __init__(self, f8bit=False):
        self.f8bit = f8bit
        if f8bit:  # 8bit mode
            self.CSI = '\x9b'
        else:
            self.CSI = '\x1b['

    def draw(self, image, columns=62, rows=None,
             negate=False, use_unicode=False,
             output=sys.stdout,
             ncolor=1):
        drcs_converter = DrcsConverter(image, self.f8bit,
                                       columns, rows, negate,
                                       use_unicode,
                                       ncolor=ncolor)
        drcs_converter.write(output)
