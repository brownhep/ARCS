import ROOT as R
from Methods import *
#from CalibrateSensors import *
import time
import sys

R.gROOT.ProcessLine('.L LandauFit.C+')

#param_file = "/home/alanman/configs/unirr_R11_config"
#param_file = "/home/alanman/configs/unirr_R12_config"
#param_file = "/home/alanman/configs/unirr_R5_config"
#param_file = "/home/alanman/configs/unirr_R7_config"

#param_file = "/home/alanman/configs/test_unirr"
#param_file = "/home/alanman/configs/test_irr"

#param_file = "/home/alanman/configs/irr_config"
#param_file = "/home/alanman/configs/irr_200Y_4_config_R12"
#param_file = "/home/alanman/configs/irr_200Y_4_config_R2"
#param_file = "/home/alanman/configs/irr_320Y_5_config_R3"

#param_file = "/home/alanman/configs/unirr_config"
#param_file = "/home/alanman/configs/test_config"

#param_file = "/home/alanman/configs/unirr_200N_config_R6"
param_file = "/home/espencer/configs/unirr_200N_config_R10_B"
#param_file = "/home/alanman/configs/unirr_200N_1samp_config_R5"
#param_file = "/home/alanman/configs/unirr_config_200N_config_R8"


# Read in run parameters from the param_file
params = read_params(param_file)

runMin = params['runMin']
runMax = params['runMax']

if "good_chans" in params:
    good_chans = params['good_chans']
else:
    good_chans = range(32)

if "three_sample" in params:
    three_sample = 'True' == params["three_sample"];
else:
    three_sample = False

#If given, set the minimum and maximum run numbers.
if len(sys.argv) == 3:
	runMin = sys.argv[1]    #The minimum and maximum run numbers to look at.
	runMax = sys.argv[2]

runNumbers = range(int(runMin),int(runMax)+1)

if len(sys.argv) > 3:
	runNumbers = [int(i) for i in sys.argv[1:]]

#scale allows for conversion of ADC counts to another value. The 192k value is ~num electrons.
#scale = 192000/255
scale = 1


#Set up the TTree for holding results:
runno = array('i',[0])
rgn = array('i',[0])
strip = array('i',[0])
badch = array('i',[0])
pd = array('f',[0.])
noise = array('f',[0.])

RTree = R.TTree('strips','Strip Info')
RTree.Branch('run',runno,'runno/I')
RTree.Branch('rgn',rgn,'rgn/I')
RTree.Branch('strip',strip,'strip/I')
RTree.Branch('badch',badch,'badch/I')
RTree.Branch('pd',pd,'pd/F')
RTree.Branch('noise',noise,'noise/F')


#Take in environmental data.
TFile_name = params['inFolder'] + params['filePrefix'] + '_Env.dat'
T_Array = get_tempdata(TFile_name,params['outFolder'],params['filePrefix'])

#Find bad/noisy channels from calibration
#bad_chans = cal_sensor("FTH200Y_lat4_Cal")
#print bad_chans


###Manually set bad/good channels.
#good_chans = range(19,24)  #R12 (R1 Brown) Week of Jun8
#good_chans = range(7,32)   #R2 (R11 Brown) Week of Jun1
#good_chans = range(6,14)
#good_chans = range(32)
bad_chans = [x for x in range(32) if x not in good_chans]
		####

import os
for runNum in runNumbers: 				#range(int(runMin),int(runMax)+1):
	for volt in reversed(params['volts']):

		root_name = params['filePrefix'] + "_" + str(runNum)
		#Creates Root File for each voltage to store Plots 
		RFile_name = params['outFolder'] + root_name + '.root'
		RFile = R.TFile(RFile_name, 'RECREATE')
		RFile.Close()
		
		#Generates the Pre-Pedestal
		print "Prepedestal for " + root_name +", " + volt
		#preped_name = params['inFolder'] + 'Raw_Data_'+root_name + '_Ped.dat'

		preped_name = params['inFolder'] + root_name + '_Ped.dat'

		if not os.path.exists(preped_name):
			print "Missing file",preped_name
			continue
		b = os.path.getsize(preped_name)
		if b < 16e6:
			print "File too small: " + preped_name
			continue

		if not three_sample:
			preped = get_preped(preped_name, 'PrePed', RFile_name, 1)
		else:
			preped = get_preped3(preped_name, 'PrePed', RFile_name, 1)

		for region in params['regions']:
			file_name = params['inFolder']+root_name+'_Sr90.dat'
			#Generates Pedestal from Signal Data
			print "Pedestal for " + root_name +", " + volt + ", R" + region
			if not three_sample:
				ped = get_pedestal(file_name, int(region), preped, 'R'+region,RFile_name,scale)
			else:
				ped = get_pedestal3(file_name, int(region), preped, 'R'+region,RFile_name,scale)
	
			if not os.path.exists(file_name):
				continue
			b = os.path.getsize(file_name)
			if b < 15e6:
				print "File too small: " + preped_name
				continue

			#Locates the bad Channels
		#	bad_chans = []
		#	bad_chans = find_bad_chans(file_name, int(region), ped, 'R'+region,RFile_name,scale)

			#Fill Tree of Strip Information
			for x in xrange(32):
				y = 32*(int(region)+1)+x
				runno[0] = runNum
				rgn[0] = int(region)
				strip[0] = y
				badch[0] = 0
				if x in bad_chans:  badch[0] = 1
				pd[0] = preped.GetBinContent(y+1) #Was running off ped instead of preped
				noise[0] = preped.GetBinError(y+1)*R.sqrt(preped.GetBinEntries(y+1))
				RTree.Fill()
	#		import pickle
	#		pickle.dump(preped,open("preped.pkl","w"))
	#		preped = pickle.load(open("preped.pkl",'r'))

			print "Bad chans: ", bad_chans
			if not three_sample:
				get_signal(file_name, int(region), preped, 'R'+region,RFile_name,bad_chans, runNum, scale, T_Array)
				print "Do Landau fit:"
				print ' Run #',runNum,', V: ', volt, ', Region: ', region
				doSimpleLandau(RFile_name, int(region), start=10)
			else:
				get_signal3(file_name, int(region), preped, 'R'+region,RFile_name,bad_chans, runNum, scale, T_Array)
				print "Do Landau fit:"
				print ' Run #',runNum,', V: ', volt, ', Region: ', region
				doSimpleLandau3(RFile_name, int(region), start=10)


#RStrip_Name = params['filePrefix'] + '_StripInfo.root'
#RStripFile = R.TFile(RStrip_Name,'RECREATE')
#RTree.Write()
#RStripFile.Close()

