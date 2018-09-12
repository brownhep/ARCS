#import ROOT as R
from Methods import *
#import time
import os.path

runinfo = sys.argv[1]    #ex: FTH200P_LTR10
#folder = sys.argv[2]	#Where data files are stored. ex: '/home/dtersegno/Raw_Data/LongTerm/FTH200P_R10/'
#runMin = sys.argv[1]    #The minimum and maximum run numbers tolook at.
#runMax = sys.argv[2]

#runMinstr = input("Enter beginning run number: ")
#runMaxstr = input("Enter end run number: ")
#runMin = str(runMinstr)
#runMax = str(runMaxstr)
#Get Run information from currentruninfo.txt

#runinfo = ""
if runinfo == "": runinfo = "currentruninfo.txt"
f = open(runinfo,"r")
filePrefix = f.readline()[:-1]
folder = f.readline()[:-1]
outfolder = f.readline()[:-1]
regline = f.readline()[:-1]
regions = regline.split(' ')
vline = f.readline()[:-1]
Volts = vline.split(' ')
runMin = f.readline()[:-1]
runMax = f.readline()[:-1]
print filePrefix, folder, regions, Volts
f.close()


TFile_name = folder + filePrefix + '_Env.dat'
T_Array = get_tempdata(TFile_name, outfolder, filePrefix)

haddstr = "hadd -f " + outfolder + filePrefix + "_hd.root"
for runNum in range(int(runMin),int(runMax)+1):
	for volt in reversed(Volts):

		#if os.path.isfile(outfolder+filePrefix+"_T"+str(runNum)+".root"): root_name = filePrefix + "_T" + str(runNum)
		#else: root_name = filePrefix + "_" + str(runNum)
		root_name = filePrefix + "_" + str(runNum)
		#Creates Root File for each voltage to store Plots 
		RFile_name = outfolder + root_name + '_hd.root'
		haddstr += " " + RFile_name

fout = open("analysisshell","w")
fout.write("#!/bin/bash \n")
#fout.write(haddstr + "\n")
fout.write("python dolandau.py " + runMin + " " + runMax + " " + "currentruninfo.txt" + "\n")
fout.write("python strip_info.py " + runMin + " " + runMax + " " + "currentruninfo.txt" + "\n")
fout.write("python LongTermData.py " + "currentruninfo.txt" + "\n")
fout.write("python HitDataPlots.py currentruninfo.txt\n")
fout.close()

fout = open("haddshell","w")
fout.write("#!/bin/bash \n")
fout.write(haddstr + "\n")
fout.close()

