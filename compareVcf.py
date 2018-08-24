#!/usr/bin/env python

import sys
from os import path

# Validate arguments
if len(sys.argv) < 3 or len(sys.argv) > 4:
	sys.stderr.write("Usage: {0} file1.vcf file2.vcf [output.txt]\
		\nOR (if you would like metadata to be included in output file): {0} file1.vcf file2.vcf > output.txt\n".format(sys.argv[0]))
	sys.exit(1)

if len(sys.argv) == 4:
	outfile = open(sys.argv[3], 'w')
else:
	outfile = sys.stdout

totalsubs = 0
totalindels = 0

# Get a list of VCF entries from a VCF file containing (pos, ref, alt)
def parseFile(f):
	nsubs = 0
	nindels = 0
	entryDict = {}
	with open(f) as fp:
		for line in fp:
			if line.startswith('#'):
				continue
			entry = line.split('\t')
			pos = int(entry[1])
			if pos not in entryDict:
				entryDict[pos] = []
			for var in entry[4].split(','):
				entryDict[pos].append((entry[3], var))
			if len(entry[3]) == 1 and len(entry[4]) == 1:
				nsubs += 1
			else:
				nindels += 1

	fname = path.basename(f)
	sys.stdout.write("# Found {} entries ({} substitutions, {} indels) in {}\n".format(nsubs+nindels, nsubs, nindels, fname))
	return (entryDict, nsubs, nindels)

f1 = sys.argv[1]
f2 = sys.argv[2]

parse1 = parseFile(f1)
data1 = parse1[0]
totalsubs += parse1[1]
totalindels += parse1[2]
parse2 = parseFile(f2)
data2 = parse2[0]
totalsubs += parse2[1]
totalindels += parse2[2]

# Lee-way in the difference of variant position
delta = 20

processed = []
matches = []
mismatches = []
# Found in 1 but not 2
missing1_2 = []
# Found in 2 but not 1
missing2_1 = []
submatches = 0
indelmatches = 0

for pos1, varlist1 in data1.items():
	for var1 in varlist1:
		found = []
		matchFound = False
		for pos2 in range(pos1 - delta, pos1 + delta + 1):
			if pos2 in data2:
				found.append(pos2)
				varlist2 = data2[pos2]
				for var2 in varlist2:
					if var1 == var2:
						matchFound = True
						matches.append(("{}/{}".format(pos1,pos2), var1))
						if len(var1[0]) == len(var1[1]):
							submatches += 1
						else:
							indelmatches += 1
						break
				if matchFound:
					break


		if len(found) > 0 and not matchFound:
			mmvarlist = [data2[i] for i in found]
			possibleMismatches = ""
			for pos in found:
				for mmvar in data2[pos]:
					possibleMismatches += "{pos},{mmvar}\t".format(pos=pos, mmvar=mmvar)
			mismatches.append("{pos},{var} : {allmismatches}".format(pos=pos1, var=var1, allmismatches=possibleMismatches))

	if len(found) == 0:
		missing1_2.append(pos1)


for pos2, varlist2 in data2.items():
	for var2 in varlist2:
		found = False
		for i in range(pos2 - delta, pos2 + delta + 1):
			if i in data1:
				found = True
		if not found:
			missing2_1.append(pos2)

nEntries = totalsubs + totalindels
percentMatch = (len(matches) * 2) / nEntries
percentMismatch = (len(mismatches) * 2) / nEntries

sys.stdout.write("# {} matches ({:.0%})\n# {} mismatches ({:.0%})\n# {} missing entries found in {f1} but not {f2}\n\
# {} missing entries found in {f2} but not {f1}\n".format(len(matches)*2, percentMatch, len(mismatches)*2, percentMismatch, len(missing1_2), len(missing2_1), f1=f1, f2=f2))
sys.stdout.write("# {}/{} ({:.0%}) matching substitutions\n# {}/{} ({:.0%}) matching indels\n".format(submatches*2,totalsubs, submatches*2/totalsubs, indelmatches*2,totalindels, indelmatches*2/totalindels))
# sys.stdout.write("# {:.0%} matching substitutions\n# {:.0%} matching indels\n".format(submatches*2/totalsubs, indelmatches*2/totalindels))

for m in matches:
	outfile.write("MATCH: {}\n".format(str(m)))

for nm in mismatches:
	outfile.write("MISMATCH: {}\n".format(str(nm)))

for missing in missing1_2:
	outfile.write("MISSING1_2: {}\n".format(str(missing)))

for missing in missing2_1:
	outfile.write("MISSING2_1: {}\n".format(str(missing)))


outfile.close()