import os
import glob
import numpy as np

# read in data from pscan_output.dat to know how many directories we are dealing with
#output_filename = '~/shape_modelling/162p/batch_convexinv/pscan_output.dat'
#f = open(output_filename, 'r')
#nonempty_lines = [line.strip("\n") for line in f if line != "\n"]
#njobs = len(nonempty_lines)
#f.close()

#for j in range(1,njobs+1):
#print(j)
#dir_use = 'polescan%d'%(j)
dir_use = os.getcwd()
#print('\n')
#print('Working in directory', dir_use)

input_lc_file = '~/shape_modelling/162p/162P_LC_dist_cal_NU.dat'
files = sorted(glob.glob(dir_use+'/input_convex_pars*'))

for i, file in enumerate(files):
    l = file.index('pars')
    coords = (file[l+4:])
    #print(coords)

    conv_rep = dir_use+'/convex_report'+coords
    output_pars = dir_use+'/output_convex_pars'+coords
    output_lcs = dir_use+'/output_lcs'+coords
    #print(conv_rep)
    os.system('cat %s | ~/software/convexinv/Convexinv/convexinv -v > %s -p %s %s %s'%(input_lc_file, conv_rep, output_pars, file, output_lcs))
    print('Finished with %s!'%coords[1:], len(files)-(i+1),'files to go!')
