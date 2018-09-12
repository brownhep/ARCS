import ROOT as R
from Methods_cuttest import *
from CalibrateSensors import *
import time

#R.gROOT.ProcessLine('.L Code/LandauFit.C+')

#filePrefix = sys.argv[1]    #ex: FTH200P_LTR10
#folder = sys.argv[2]	#Where data files are stored. ex: '/home/dtersegno/Raw_Data/LongTerm/FTH200P_R10/'
runMin = sys.argv[1]    #The minimum and maximum run numbers tolook at.
runMax = sys.argv[2]

getEta = 0

#scale allows for conversion of ADC counts to another value. The 192k value is ~num electrons.
#scale = 192000/255
scale = 1

runno = array('i',[0])
rgn = array('i',[0])
strip = array('i',[0])
badch = array('i',[0])
pd = array('f',[0.])
noise = array('f',[0.])

numsteps = 30
stepsize = 0.3
hitperevt = R.TGraph(numsteps)
avghitstrip = R.TGraph(numsteps)
noisyevts = R.TGraph(numsteps)

RTree = R.TTree('strips','Strip Info')
RTree.Branch('run',runno,'runno/I')
RTree.Branch('rgn',rgn,'rgn/I')
RTree.Branch('strip',strip,'strip/I')
RTree.Branch('badch',badch,'badch/I')
RTree.Branch('pd',pd,'pd/F')
RTree.Branch('noise',noise,'noise/F')

	 
#Get Run information from currentruninfo.txt
f = open("currentruninfo.txt","r")
filePrefix = f.readline()[:-1]
folder = f.readline()[:-1]
outfolder = f.readline()[:-1]
regline = f.readline()[:-1]
regions = regline.split(' ')
vline = f.readline()[:-1]
Volts = vline.split(' ')
print filePrefix, folder, regions, Volts
f.close()

TFile_name = folder + filePrefix + '_Env.dat'
T_Array = get_tempdata(TFile_name, outfolder, filePrefix)

#Find bad/noisy channels from calibration
#bad_chans = cal_sensor("FTH200Y_lat4_Cal")
#print bad_chans
bad_chans = [159,193]

for runNum in range(int(runMin),int(runMax)+1):
	for volt in reversed(Volts):

		root_name = filePrefix + "_" + str(runNum)
		#Creates Root File for each voltage to store Plots 
		RFile_name = outfolder + root_name + '.root'
		RFile = R.TFile(RFile_name, 'RECREATE')
		RFile.Close()


		for i in regions:
			#Generates the Pre-Pedestal
			print "Prepedestal for " + root_name +", " + volt
			#preped_name = folder + 'Raw_Data_'+root_name + '_Ped.dat'
			preped_name = folder + root_name + '_Ped.dat'
			preped = get_preped(preped_name, 'PrePed', int(i), RFile_name, 1)
			file_name = folder+root_name+'_Sr90.dat'

			#Fill Tree of Strip Information
			for x in xrange(32):
				y = 32*(int(i)+1)+x
				runno[0] = runNum
				rgn[0] = int(i)
				strip[0] = y
				badch[0] = 0
				#if x in bad_chans:  badch[0] = 1
				pd[0] = preped.GetBinContent(y+1) #Was running off ped instead of preped
				noise[0] = preped.GetBinError(y+1)*R.sqrt(preped.GetBinEntries(y+1))
				#print 'preped', x, preped.GetBinContent(y+1),preped.GetBinError(y+1)*R.sqrt(ped.GetBinEntries(y+1)), preped.GetBinEntries(y+1)
				#print 'ped   ', x, ped.GetBinContent(y+1),ped.GetBinError(y+1)*R.sqrt(ped.GetBinEntries(y+1)), ped.GetBinEntries(y+1)
				RTree.Fill()
				
			for x in xrange(numsteps):
				hits = get_signal(file_name, int(i), preped, 'R'+str(13-int(i)),RFile_name,bad_chans, runNum, x*0.3, scale, T_Array) # *****Try running off preped***** 
				hitperevt.SetPoint(x, x*stepsize, hits[0])
				avghitstrip.SetPoint(x, x*stepsize, hits[1])
				noisyevts.SetPoint(x,x*stepsize, hits[2])

RStrip_Name = filePrefix + '_cuttest.root'
RStripFile = R.TFile(RStrip_Name,'RECREATE')
hitperevt.Write("Hits")
avghitstrip.Write("Strips")
noisyevts.Write("NoisyEvts")
RStripFile.Close()

