PyDRCS
=======

Install
-------

via github ::

    $ git clone https://github.com/saitoha/PyDRCS.git pydrcs
    $ cd pydrcs 
    $ python setup.py install

or via pip ::

    $ pip install PyDRCS

Usage
-----

Command line tool::

    $ drcsconv [options] filename

or ::

    $ cat filename | drcsconv [options]


* Options::

  -h, --help                    show this help message and exit
  -8, --8bit-mode               Generate a DRCS image for 8bit terminal or printer
  -7, --7bit-mode               Generate a DRCS image for 7bit terminal or printer
  -u, --unicode                 Use drcsterm's DRCS-unicode mapping
  -n, --negate                  Negate image
  -c COLUMNS, --columns=COLUMNS Image width in cell size (default=62, max=62)
  -r ROWS, --rows=ROWS          Image height in cell size
  -t, --text                    Interpret input stream as a text run
  -f FONT, --font=FONT          Specifies the absolute path of font file if -t option is set (default: GNU unifont)
  --version                     show version


Code Example
------------

::

    from drcs import DrcsWriter
    writer = DrcsWriter()
    writer.draw('test.png') 

Dependency
----------
 - Python Imaging Library (PIL)
   http://www.pythonware.com/products/pil/ 

 - wcwidth.py
   https://svn.wso2.org/repos/wso2/carbon/platform/trunk/dependencies/cassandra/pylib/cqlshlib/wcwidth.py
   (Licensed under Apache License 2.0)

 - GNU Unifont Glyphs
   http://unifoundry.com/unifont.html

Reference
---------
 - VT320 Soft Character Sets
   http://vt100.net/dec/vt320/soft_characters

 - DECDLD
   http://vt100.net/docs/vt510-rm/DECDLD

