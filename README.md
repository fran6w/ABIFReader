# ABIFReader
Python ABIF reader

Python implementation of an ABIF file reader according to Applied Biosystems' specificatons,
see http://www.appliedbiosystems.com/support/software_community/ABIF_File_Format.pdf

This code is published by Interactive Biosoftware, France,
see http://www.interactive-biosoftware.com/
under LGPL license,
see http://www.gnu.org/licenses/lgpl-3.0.en.html

Author: Francis Wolinski
Version: 1.0.2, October 2017
Copyright (c) Francis Wolinski 2007-2017

## User Manual

Conversion of ABIF data types to Python types (see struct.unpack method)

- type 1 = byte -> integer
- type 2 = char -> string
- type 3 = word -> long
- type 4 = short -> integer
- type 5 = long -> integer
- type 7 = float -> float
- type 8 = double -> float
- type 10 = date -> datetime.date instance
- type 11 = time -> datetime.time instance
- type 12 = thumb -> tuple
- type 13 = bool -> True or False
- type 18 = pString -> string
- type 19 = cString -> string
- type = 1024+ = user -> NotImplemented: to be overwritten in user's code in ABIFReader.readNextUserData method
- type = other -> NotImplemented

## Exemple

```
from ABIFReader import *
reader = ABIFReader(<filename>)  # creates an instance of ABIFReader
reader.version  # version of ABIF file
reader.showEntries()  # print all entries of ABIF file "<name> (<num>) / <type> (<size>)"
data = reader.getData(<name>[, <num>])  # read data for entry named <name> with number <num>, by default <num> is 1
reader.close()  # close the file, since it is kept open
```
