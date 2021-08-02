#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 26 15:53:18 2020

@author: Abbie Donaldson (based on script by A.R.)

Edited June 2021: This script is for running multiple pole scans via batch scripts.
Distance calibrated lightcurves
Input period and k value need to be read from pscan_output.dat
This script generates the input files in their respective folders, then call ADDME.sh to run mutliple pole scans.

"""

import sys
import time
import os
import glob
import numpy as np
import getpass
import subprocess

convexinv = '~/software/convexinv/Convexinv/convexinv' #full path to the convexinv program itself

# Reading in necessary data from pscan_output
pscan_filename = '~/Documents/year1/shape_modelling/162p/batch_convexinv/pscan_output.dat'
f = open(pscan_filename, 'r')
lines = f.readlines()
period_list = []
chi_list = []
k_list = []
for line in lines:
	data = line.split()
	period_list.append(float(data[0]))
	chi_list.append(float(data[1]))
	k_list.append(float(data[2]))

# Number of jobs to run = length of above lists
njobs = len(period_list)

##### ----- CHANGE ME ----- #####
input_lc_file = '~/Documents/year1/shape_modelling/162p/162P_LC_dist_cal_NU.dat'
##### ----- CHANGED ME? -----#####

ast_jd = 2454238.450 # JD0 in 2007 for the full data set

# Create grid of lambdas and bets based on CL args
def make_input(lamb,beta,period,jd,iteration):
	return "%d           0    inital lambda [deg] (0/1 - fixed/free)\n%d           0    initial beta [deg] (0/1 - fixed/free)\n%f      0    inital period [hours] (0/1 - fixed/free)\n %f      zero time [JD]             \n0            initial rotation angle [deg]             \n0.1            convexity regularization\n6 6            degree and order of spherical harmonics expansion\n8            number of rows                            \n%f        %d    phase funct. param. 'a' (0/1 - fixed/free)          \n%f        %d    phase funct. param. 'd' (0/1 - fixed/free)         \n%f        %d    phase funct. param. 'k' (0/1 - fixed/free)         \n0.1        0    Lambert coefficient 'c' (0/1 - fixed/free)\n%d        iteration stop condition            \n"%(lamb,beta,period,jd,a,ai,d,di,k,ki,iteration)

if (len(sys.argv) != 8):
    print('Incorrect number of arguments, call as:')
    print('python run_multiple.py <low lamb> <high lamb> <lamb step> <low beta> <high beta> <beta step> <termination iteration>')
    sys.exit()

try:
	lamb_low = float(sys.argv[1])
	lamb_high = float(sys.argv[2])
	lamb_step = float(sys.argv[3])
	beta_low = float(sys.argv[4])
	beta_high = float(sys.argv[5])
	beta_step = float(sys.argv[6])
	iterations = float(sys.argv[7])
except:
	#...if this fails somehow, inform user
	print('Problem parsing your inputs - I tried to convert them all to floats but I couldnt :( ')
	sys.exit()

#initialise arrays for storing all combinations
full_lambs = []
full_betas = []

#for every lamb and beta pairing in the range provided, add to the full lists
for lamb in np.arange(lamb_low,lamb_high+0.5*lamb_step,lamb_step):
	for beta in np.arange(beta_low,beta_high+0.5*beta_step,beta_step):
		full_lambs.append(lamb)
		full_betas.append(beta)

# Generate input files in separate directory for every period and k value read in
for i in range(len(period_list)):
	ast_period = period_list[i]

	# Define scattering params to save me having to scroll through the function below in vim:
	# Params: a,d,k; Each param has index ai, di, ki = 0/1 (fixed/free)

	a = 0
	ai = 0
	d = 0
	di = 0
	k = k_list[i]
	ki = 1

	root_dir = os.getcwd() #finds the pwd

	#increments a counter, cycles round once limit value is reached; should really be done with modulo.
	def cycle(value,limit):
		newvalue = value+1 if value+1 < limit else value+1 - limit
		return newvalue


	#input file text, with formatting statements for insertion of relevant parameter values


	#echo info so far to screen
	print('This trial is for k = %f and period = %f h'%(k_list[i], period_list[i]))
	print('Range of Lambda = %d - %d in steps of size %d'%(lamb_low, lamb_high,lamb_step))
	print('Range of Beta = %d - %d in steps of size %d'%(beta_low, beta_high,beta_step))
	print('Total no. coordinate combinations to process: %d'%(len(full_betas)))


	# Create 'polescan' folder for each instance
	print('Directory in which files are being created:', root_dir)
	print('\n')

	dir_name = 'polescan%d'%(i+1)
	#print(dir_name)
# Remove existing directory if it exists:
	if os.path.exists(dir_name):
		os.system('rm -rf %s'%(dir_name))
		os.mkdir(dir_name)
	else:
		os.mkdir(dir_name)

	for lamb, beta in zip(full_lambs, full_betas):
	    #print(lamb,beta)
	    #...generate suitable input file
	    fout = open("%s/input_convex_pars_%d_%d"%(dir_name,lamb,beta),'w+')
	    fout.write(make_input(lamb,beta,ast_period,ast_jd,iterations))
	    fout.close()

	dir_use = dir_name

	files = sorted(glob.glob(dir_use+'/input*'))

	# initialise log file, and populate with some basic setup info.
	logfile = open('%s/log.txt'%(dir_use),'w')
	logfile.write("Hello, and welcome to this log file, we hope you enjoy your stay!\n")
	logfile.write("input lc file = %s\n"%(input_lc_file))
	logfile.write("program file = %s\n"%(convexinv))
	logfile.write("period = %s\n"%(ast_period))
	logfile.write("JD = %s\n"%(ast_jd))

	logfile.write("lambda (high, low, step) (%d,%d,%d)\n"%(lamb_low,lamb_high,lamb_step))
	logfile.write("beta (high, low, step) (%d,%d,%d)\n"%(beta_low,beta_high,beta_step))
	logfile.write("terminate at iteration no. %d\n"%(iterations))
	logfile.write("Starting LS params: (%f,%f,%f), (%d,%d,%d)\n"%(a,d,k,ai,di,ki))
	logfile.write("Run the following in data directory:\n")
	logfile.write("~/software/convexinv_scripts/generate_chi_reports.sh %d %d %d %d %d %d %d \n"%(iterations,lamb_low,lamb_high,lamb_step,beta_low,beta_high,beta_step))
	logfile.write("%i files to process in this run \n"%len(full_betas))
	logfile.write("---------\n")

	#finalise log file
	logfile.close()

