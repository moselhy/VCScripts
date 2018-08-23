#!/usr/bin/env python

import sys
import os

if len(sys.argv) != 4:
    print("Usage: {} (string)filename.fastq (string)readID (int)numreads".format(sys.argv[0]))
    sys.exit(1)

filepath = sys.argv[1]
readID = sys.argv[2]
numreads = int(sys.argv[3])

filename = os.path.splitext(filepath)[0]
newfilepath = "{}_new.fastq".format(filename)

with open(filepath, 'r') as fpread, open(newfilepath, 'w') as fpwrite:
    for line in fpread:
        if line.startswith(readID):
            numreads-=1
        if numreads >= 0:
            fpwrite.write(line)

