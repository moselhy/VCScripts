#!/bin/bash

if [ $# != 1 ]; then
	echo "Usage: $0 outfile.txt"
else
	mysql --user=genome --host=genome-euro-mysql.soe.ucsc.edu -A -P 3306 -D hg38 -e 'SELECT chrom, chromStart, class, refNCBI, observed FROM snp150Common' > $1
fi