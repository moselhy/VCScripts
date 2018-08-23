#!/usr/bin/env python

import sys
from sys import stdin
from GenomeParser import GenomeParser

if len(sys.argv) != 2:
	print("Usage: {} genome.fasta".format(sys.argv[0]))
	sys.exit(1)

filename = sys.argv[1]

gp = GenomeParser(filename)

def printNuc(s):
	print('=>\'{}\'\n'.format(s))

for line in stdin:
	printNuc(gp.getNuc(line))