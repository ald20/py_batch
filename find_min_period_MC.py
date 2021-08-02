import numpy as np
import glob
import os
import sys

if len(sys.argv)<2:
   print("Call as find_min_period_MC.py + no. directories (int))
   sys.exit()

rootdir = "~/Documents/year1/shape_modelling/162p/batch_convexinv"
ndirs = int(sys.argv[1])
file = open('%s/pscan_output.dat'%rootdir, 'w')

for i in range(1,ndirs+1):
    period = []
    chi = []
    output_periods = rootdir+"/period_scan%d/output_periods_162p"%(i)
    input_data = rootdir+"/period_scan%d/input_period_001"%(i)
    # Read contents of file
    f = open(output_periods, 'r')
    lines = f.readlines()
    for line in lines:
        data = line.split()
        period.append(float(data[0]))
        chi.append(float(data[2]))
    chi_min = min(chi)
    for j in range(len(chi)):
        if chi[j] == chi_min:
            period_min = period[j]
    f.close()
    f = open(input_data, 'r') # Want to also output the starting k value to make tracking a wee bit easier :)
    inpdat = []
    lines = f.readlines()
    for line in lines:
        data = line.split()
        inpdat.append(float(data[0]))
    print(period_min, chi_min, inpdat[6])

    # Write line to output file containing data we have just obtained

    file.write("%6f %f %f\n"%(period_min, chi_min, inpdat[6]))
file.close()
