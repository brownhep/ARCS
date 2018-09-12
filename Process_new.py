import ROOT as R
from Methods import *
from CalibrateSensors import *
import time
import sys

R.gROOT.ProcessLine('.L LandauFit.C+')

param_file = "/home/alanman/test_irr"
#param_file = "/home/alanman/current_run"
#param_file = "../test_run"
#param_file = "../past_runs/WeekOfJun1_R2"

# Read in run parameters from the param_file
params = {}
with open (param_file) as f:
	for line in f:
		if line[:1] == "#" or len(line) == 0: continue
		try:
			(key, val) = [x.strip() for x in line.split(":")]
		except ValueError:
			pass
		if key == "regions" or key == "volts":
			val = val.split(" ")
		params[key] = val
		if key == "good_chans":
		   #Parse the line
			ls = []
			for s in val.split(" "):
			   s = s.strip()
			   if s[0] == "(":
				x = s[s.find("(")+1:s.find(")")].split(",")
				ls.extend(range(int(x[0]),int(x[1])))
			   else:
				ls.append(int(s))
			params[key] = ls
		key, val = "", ""


runMin = params['runMin']
runMax = params['runMax']

if "good_chans" in params:
    good_chans = params['good_chans']
else:
    good_chans = range(32)

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
T_Array = get_tempdata(TFile_name, params['outFolder'], params['filePrefix'])

#Find bad/noisy channels from calibration
#bad_chans = cal_sensor("FTH200Y_lat4_Cal")
#print bad_chans


###Manually set bad/good channels.
#good_chans = range(19,24)  #R12 (R1 Brown) Week of Jun8
#good_chans = range(7,32)   #R2 (R11 Brown) Week of Jun1
good_chans = range(32)
bad_chans = [x for x in range(32) if x not in good_chans]
bad_chans = [0,1,2]
		####


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
		preped = get_preped(preped_name, 'PrePed', RFile_name, 1)

		for region in params['regions']:
			file_name = params['inFolder']+root_name+'_Sr90.dat'
			#Generates Pedestal from Signal Data
			print "Pedestal for " + root_name +", " + volt + ", R" + region
			ped = get_pedestal(file_name, int(region), preped, 'R'+region,RFile_name,scale)
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
			

			print "Bad chans: ", bad_chans

			get_signal(file_name, int(region), preped, 'R'+region,RFile_name,bad_chans, runNum, scale, T_Array)
			print "Do Landau fit:"
			print ' Run #',runNum,', V: ', volt, ', Region: ', region
			doSimpleLandau(RFile_name, int(region), start=10)
	
RStrip_Name = params['filePrefix'] + '_StripInfo.root'
RStripFile = R.TFile(RStrip_Name,'RECREATE')
RTree.Write()
RStripFile.Close()

