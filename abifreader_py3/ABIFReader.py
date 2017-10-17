# Python implementation of an ABIF file reader according to Applied Biosystems' specificatons,
# see http://www.appliedbiosystems.com/support/software_community/ABIF_File_Format.pdf
#
# This code is published by Interactive Biosoftware, France,
# see http://www.interactive-biosoftware.com/
# under LGPL license,
# see http://www.gnu.org/licenses/lgpl-3.0.en.html
#
# Author: Francis Wolinski
# Version: 1.0.1, October 2013
# Copyright (c) Francis Wolinski 2007-2013
#
# User Manual
#
# Conversion of ABIF data types to Python types (see struct.unpack method):
# type 1 = byte -> integer
# type 2 = char -> string
# type 3 = word -> long
# type 4 = short -> integer
# type 5 = long -> integer
# type 7 = float -> float
# type 8 = double -> float
# type 10 = date -> datetime.date instance
# type 11 = time -> datetime.time instance
# type 12 = thumb -> tuple
# type 13 = bool -> True or False
# type 18 = pString -> string
# type 19 = cString -> string
# type = 1024+ = user -> NotImplemented: to be overwritten in user's code in ABIFReader.readNextUserData method
# type = other -> NotImplemented
#
# from ABIFReader import *
# reader = ABIFReader(<filename>) # creates an instance of ABIFReader
# reader.version # version of ABIF file
# reader.showEntries() # print all entries of ABIF file "<name> (<num>) / <type> (<size>)"
# data = reader.getData(<name>[, <num>]) # read data for entry named <name> with number <num>, by default <num> is 1
# reader.close() # close the file, since it is kept open

import struct
import datetime

ABIF_TYPES = {
    1: 'byte', 2: 'char', 3: 'word', 4: 'short', 5: 'long', 7: 'float', 8: 'double',
    10: 'date', 11: 'time', 12: 'thumb', 13: 'bool', 18: 'pString', 19: 'cString'
    }


class ABIFReader:
    def __init__(self, fn):
        self.filename = fn
        self.file = open(fn, 'rb')
        self.type = self.readNextString(4)
        if self.type != 'ABIF':
            self.close()
            raise SystemExit("error: No ABIF file '%s'" % fn)
        self.version = self.readNextShort()
        dir = DirEntry(self)
        self.seek(dir.dataoffset)
        self.entries = [DirEntry(self) for i in range(dir.numelements)]

    def getData(self, name, num=1):
        entry = self.getEntry(name, num)
        if not entry:
            raise SystemExit("error: Entry '%s (%i)' not found in '%s'" % (name, num, self.filename))
        self.seek(entry.mydataoffset())
        data = self.readData(entry.elementtype, entry.numelements)
        if data != NotImplemented and len(data) == 1:
            return data[0]
        else:
            return data

    def showEntries(self):
        for e in self.entries:
            print(e)

    def getEntry(self, name, num):
        for e in self.entries:
            if e.name == name and e.number == num:
                return e
        return None

    def readData(self, type, num):
        if type == 1:
            return [self.readNextByte() for i in range(num)]
        elif type == 2:
            return self.readNextString(num)
        elif type == 3:
            return [self.readNextUnsignedInt() for i in range(num)]
        elif type == 4:
            return [self.readNextShort() for i in range(num)]
        elif type == 5:
            return [self.readNextLong() for i in range(num)]
        elif type == 7:
            return [self.readNextFloat() for i in range(num)]
        elif type == 8:
            return [self.readNextDouble() for i in range(num)]
        elif type == 10:
            return [self.readNextDate() for i in range(num)]
        elif type == 11:
            return [self.readNextTime() for i in range(num)]
        elif type == 12:
            return [self.readNextThumb() for i in range(num)]
        elif type == 13:
            return [self.readNextBool() for i in range(num)]
        elif type == 18:
            return self.readNextpString()
        elif type == 19:
            return self.readNextcString()
        elif type >= 1024:
            return self.readNextUserData(type, num)
        else:
            return NotImplemented

    def readNextBool(self):
        return readNextByte(self) == 1

    def readNextByte(self):
        return self.primUnpack('B', 1)

    def readNextChar(self):
        return self.primUnpack('c', 1)

    def readNextcString(self):
        chars = []
        while True:
            c = self.readNextChar()
            if ord(c) == 0:
                return ''.join(chars)
            else:
                chars.append(c)

    def readNextDate(self):
        return datetime.date(self.readNextShort(), self.readNextByte(), self.readNextByte())

    def readNextDouble(self):
        return self.primUnpack('>d', 8)

    def readNextInt(self):
        return self.primUnpack('>i', 4)

    def readNextFloat(self):
        return self.primUnpack('>f', 4)

    def readNextLong(self):
        return self.primUnpack('>l', 4)

    def readNextpString(self):
        nb = self.readNextByte()
        chars = [self.readNextChar() for i in range(nb)]
        return ''.join(chars)

    def readNextShort(self):
        return self.primUnpack('>h', 2)

    def readNextString(self, size):
        chars = [self.readNextChar() for i in range(size)]
        return ''.join([x.decode('ascii') for x in chars])

    def readNextThumb(self):
        return (self.readNextLong(), self.readNextLong(), self.readNextByte(), self.readNextByte())

    def readNextTime(self):
        return datetime.time(self.readNextByte(), self.readNextByte(), self.readNextByte(), self.readNextByte()*10000)

    def readNextUnsignedInt(self):
        return self.primUnpack('>I', 4)

    def readNextUserData(self, type, num):
        # to be overwritten in user's code
        return NotImplemented

    def primUnpack(self, format, nb):
        x = struct.unpack(format, self.file.read(nb))
        return x[0]

    def close(self):
        self.file.close()

    def seek(self, pos):
        self.file.seek(pos)

    def tell(self):
        return self.file.tell()


class DirEntry:
    def __init__(self, reader):
        self.name = reader.readNextString(4)
        self.number = reader.readNextInt()
        self.elementtype = reader.readNextShort()
        self.elementsize = reader.readNextShort()
        self.numelements = reader.readNextInt()
        self.datasize = reader.readNextInt()
        self.dataoffsetpos = reader.tell()
        self.dataoffset = reader.readNextInt()
        self.datahandle = reader.readNextInt()

    def __str__(self):
        return "%s (%i) / %s (%i)" % (self.name, self.number, self.mytype(), self.numelements)

    def mydataoffset(self):
        if self.datasize <= 4:
            return self.dataoffsetpos
        else:
            return self.dataoffset

    def mytype(self):
        if self.elementtype < 1024:
            return ABIF_TYPES.get(self.elementtype, 'unknown')
        else:
            return 'user'


if __name__ == '__main__':
    pass