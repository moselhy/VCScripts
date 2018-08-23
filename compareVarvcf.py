#!/usr/bin/env python

""" SCRIPT TO COMPARE OUTPUT FILE FROM UPVC 1.4 TO .VAR FILES
Created by: Dr. Dominique Lavenier, INRIA, Rennes
Last modified by: Mohamed Moselhy, UWO, Canada
 """

import sys, os

if len(sys.argv) != 2:
    print("Usage: {} fileprefix".format(sys.argv[0]))
    sys.exit(1)

fvarname = sys.argv[1]+".var"
fvcfname = sys.argv[1]+".vcf"

if not os.path.exists(fvarname):
    print("File {} does not exist".format(fvarname))
    sys.exit(1)
elif not os.path.exists(fvcfname):
    print("File {} does not exist".format(fvcfname))
    sys.exit(1)

# Data in .var file
DVAR = {}
fvar = open(fvarname)
l = fvar.readline()
while l!= "":
    ll = l.split()
    # Get position
    ident = ll[1]
    # Get the type of substitution and variant
    DVAR[ident] = ll[2]+" "+ll[-2]
    l = fvar.readline()
fvar.close()

# Data in VCF file
DVCF = {}
fvcf = open(fvcfname)
l = fvcf.readline()
while l!= "":
    if l.startswith('#'):
        l = fvcf.readline()
        continue
    ll = l.split('\t')
    # Get position
    ident = ll[1]
    # Get the type of substitution and variant
    lenRef = len(ll[3])
    lenAlt = len(ll[4])
    if(lenRef == lenAlt):
        varType = 'S'
        alt = ll[4]
    elif (lenRef > lenAlt):
        varType = 'D'
        alt = ll[4][1:]
    else:
        varType = 'I'
        alt = ll[4][:-1]
    DVCF[ident] = varType+" "+alt
    l = fvcf.readline()
fvcf.close()

# true positive and false negative substitution
# create output files

ftp = open(sys.argv[1]+".tp","w")
ffn = open(sys.argv[1]+".fn","w")
# Lee-way in variant position
delta = 20
TP = 0
FN = 0
for x in DVAR:
    # Get the variant position
    ix = int(x)
    ok = False
    # Iterate through other file's variants until a match is found or until lee-way is reached
    for i in range(ix-delta,ix+delta+1):
        ident = str(i)
        # If the same variant is found in the other file, then stop there
        if ident in DVCF and DVCF[ident] == DVAR[x]:
            ok = True
            break
    # check if true positive
    if ok == True:
        TP = TP+1
        ftp.write(x.replace('_', ' ') + ' ' + DVAR[x]+"\n")
    # Otherwise, if no variant is found in the VCF file, count a false negative
    else:
        FN = FN+1
        ffn.write(x.replace('_', ' ') + ' ' + DVAR[x]+"\n")
ftp.close()
ffn.close()

# false positives
# Do the same as above but vice-versa
ffp = open(sys.argv[1]+".fp","w")
FP = 0
for x in DVCF:
    ix = int(x)
    ok = False
    for i in range(ix-delta,ix+delta):
        ident = str(i)
        if ident in DVAR and DVAR[ident] == DVCF[x]:
            ok = True
            break
    if ok == False:
        FP = FP+1
        ffp.write(x.replace('_', ' ') + ' ' + DVCF[x]+"\n")
ffp.close()

# Output results to file
ff = open(sys.argv[1]+".qlt","w")
ff.write("TP: "+str(TP)+" "+str((TP*100.0)/len(DVAR))+"\n")
ff.write("FN: "+str(FN)+" "+str((FN*100.0)/len(DVAR))+"\n")
ff.write("FP: "+str(FP)+" "+str((FP*100.0)/len(DVAR))+"\n")
ff.write("Len VAR: "+str(len(DVAR))+"\n")
ff.write("Len VCF: "+str(len(DVCF))+"\n")
ff.close()

# Output results to console
print("TP",TP, (TP*100.0)/len(DVAR))
print("FN",FN, (FN*100.0)/len(DVAR))
print("FP",FP, (FP*100.0)/len(DVAR))
print("Len VCF", len(DVCF))
print("Len VAR", len(DVAR))

