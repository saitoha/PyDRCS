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

__author__ = "Hayaki Saito (user@zuse.jp)"
__version__ = "0.1.1"
__license__ = "GPL v3"

import os
import sys
import optparse
import select
import logging
from drcs import DrcsWriter


def _printver():
        print '''
drcsconv %s
Copyright (C) 2012-2014 Hayaki Saito <user@zuse.jp>.

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


def _parse_args():

    parser = optparse.OptionParser()

    parser.add_option("-8", "--8bit-mode",
                      default=False,
                      action="store_true",
                      dest="f8bit",
                      help="Generate a drcs font image for 8bit terminal"
                           " or printer")

    parser.add_option("-7", "--7bit-mode",
                      action="store_false",
                      dest="f8bit",
                      help="Generate a drcs font image for 7bit terminal"
                           " or printer")

    parser.add_option("-n", "--negate",
                      action="store_true",
                      dest="negate",
                      default=False,
                      help="Negate image")

    parser.add_option("-u", "--unicode",
                      action="store_true",
                      dest="use_unicode",
                      default=False,
                      help="Use drcsterm's DRCS-unicode mapping")

    parser.add_option("-c", "--columns",
                      dest="columns",
                      default="62",
                      help="Image width in cell size (default=62, max=62)")

    parser.add_option("-r", "--rows",
                      dest="rows",
                      help="Image height in cell size")

    parser.add_option("-t", "--text",
                      action="store_true",
                      dest="text",
                      default=False,
                      help="Interpret input stream as a text run")

    parser.add_option("-f", "--font",
                      dest="font",
                      help="Specify the absolute path of font file if"
                           " -t option is set")

    parser.add_option("--ncolor",
                      dest="ncolor",
                      action="store",
                      type="int",
                      default=1,
                      help="Specify number of color")

    parser.add_option('--version', dest='version',
                      action="store_true", default=False,
                      help='show version')

    return parser.parse_args()


def _drawtext(options, args):

    if select.select([sys.stdin, ], [], [], 0.0):
        text = sys.stdin.read()
    elif len(args) == 0 or args[0] == '-':
        text = sys.stdin.read()

    import re
    text = re.sub('[\x00-\x1f\x7f]', '', text)

    text = unicode(text, "utf-8", "ignore")
    from PIL import Image
    from PIL import ImageDraw
    from PIL import ImageFont

    if options.font:
        fontfile = options.font
    else:
        import inspect
        name = "unifont-5.1.20080907.ttf"
        filename = inspect.getfile(inspect.currentframe())
        dirpath = os.path.abspath(os.path.dirname(filename))
        fontfile = os.path.join(dirpath, name)

    font = ImageFont.truetype(filename=fontfile,
                              size=50)
    w, h = font.getsize(text)
    image = Image.new('RGB', (w, h + 2), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    draw.text((0, 0), text, font=font, fill=(0, 0, 0))
    import wcwidth
    columns = wcwidth.wcswidth(text)
    rows = 1

    writer = DrcsWriter(f8bit=options.f8bit)
    writer.draw(image,
                columns,
                rows,
                options.negate,
                options.use_unicode,
                ncolor=options.ncolor)

def _filenize(f):
    import stat

    mode = os.fstat(f.fileno()).st_mode
    if stat.S_ISFIFO(mode) or os.isatty(f.fileno()):
        try:
            from cStringIO import StringIO
        except ImportError:
            from StringIO import StringIO
        return StringIO(f.read())
    return f


def _drawimage(options, args):

    columns = int(options.columns)
    if columns > 62:
        message = "Wrong columns value is specified (max: 62)."
        raise optparse.OptionValueError(message)

    if select.select([sys.stdin, ], [], [], 0.0):
        imagefile = _filenize(sys.stdin)
    elif len(args) == 0 or args[0] == '-':
        imagefile = _filenize(sys.stdin)
    else:
        imagefile = args[0]

    from PIL import Image  # PIL
    image = Image.open(imagefile)

    rows = options.rows
    if not rows is None:
        rows = int(rows)

    writer = DrcsWriter(f8bit=options.f8bit)
    writer.draw(image,
                columns,
                rows,
                options.negate,
                options.use_unicode,
                ncolor=options.ncolor)


def _mainimpl():

    rcdir = os.path.join(os.getenv("HOME"), ".pydrcs")
    logdir = os.path.join(rcdir, "log")
    if not os.path.exists(logdir):
        os.makedirs(logdir)

    logfile = os.path.join(logdir, "log.txt")
    logging.basicConfig(filename=logfile, filemode="w")

    try:
        options, args = _parse_args()

        if options.version:
            _printver()
            return

        if options.text:
            _drawtext(options, args)
        else:
            _drawimage(options, args)
    except optparse.OptionValueError, e:
        logging.exception(e)
        print e
    except Exception, e:
        logging.exception(e)
        print e

def main():
    _mainimpl()

if __name__ == '__main__':
    main()
