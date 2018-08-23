#!/bin/bash

# USAGE: rungatk.bash chromNumber
# Must have the following files in the working directory: CHR.fasta CHR_PE1.fastq CHR_PE2.fastq; where `CHR` is the chromosome number

# YOU MUST MODIFY THE FOLLOWING VARIABLES TO POINT TO THE CORRECT BINARIES
BWA="/local/bwa/bwa-0.7.10/bwa"
PICARD="/local/miniconda3/envs/picard-2.18.2/bin/picard"
SAMTOOLS="/local/miniconda3/envs/samtools-1.6/bin/samtools"
GATK="$HOME/bin/gatk"

# If on the GenOuest cluster, you don't need to modify the first 3 values above because the following block will load them
# (you will still need to download GATK because it is outdated on GO)...
if [ $(hostname -f | cut -d . -f2,3) == "genouest.org" ]; then
	source /local/env/envjava-1.8.0.sh
	source /local/env/envbwa-0.7.10.sh
	source /local/env/envpicard-2.18.2.sh
	source /local/env/envsamtools-1.6.sh
fi

### START PIPELINE ###

chr=$1
numcores=$(grep -c '^proc' /proc/cpuinfo)

# index the reference genome
$BWA index "chr${chr}.fasta"

# align the reads to reference and output alignment in SAM format
$BWA mem -t ${numcores} -M -R '@RG\tID:chr${chr}\tSM:chr${chr}\tPL:illumina\tLB:lib1\tPU:unit1' "chr${chr}.fasta" "chr${chr}_PE1.fastq" "chr${chr}_PE2.fastq" > aligned_reads.sam

# sort the reads by location
$PICARD SortSam INPUT=aligned_reads.sam OUTPUT=sorted_reads.bam SORT_ORDER=coordinate

# mark the duplicate reads
$PICARD MarkDuplicates INPUT=sorted_reads.bam OUTPUT=dedup_reads.bam METRICS_FILE=metrics.txt

# create the read index
$PICARD BuildBamIndex INPUT=dedup_reads.bam

# index the reference genome
$PICARD CreateSequenceDictionary R= "chr${chr}.fasta" O= "chr${chr}.dict"
$SAMTOOLS faidx "chr${chr}.fasta"

# call variants
$GATK --java-options '-Xmx32G' HaplotypeCaller -R "chr${chr}.fasta" -I "dedup_reads.bam" --output "chr${chr}_gatk.vcf"

# print output file name
echo "Created chr${chr}_gatk.vcf"

### END PIPELINE ###
