import ROOT as R
from Methods import *
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

		root_name = filePrefix + "_T" + str(runNum)
		#Creates Root File for each voltage to store Plots 
		RFile_name = outfolder + root_name + '.root'
		RFile = R.TFile(RFile_name, 'RECREATE')
		RFile.Close()


		for i in regions:
			#Generates the Pre-Pedestal
			print "Prepedestal for " + root_name +", " + volt
			preped_name = folder + 'Raw_Data_'+root_name + '_Ped.dat'
			#preped_name = folder + root_name + '_Ped.dat'
			preped = get_preped(preped_name, 'PrePed', int(i), RFile_name, 1)
			#file_name = folder+root_name+'_Sr90.dat'
			file_name = folder+'Raw_Data_'+root_name+'_R' + i + '.dat'
			#file_name+=str(i)+'.dat'  
			#Generates Pedestal from Signal Data
			print "Pedestal for " + root_name +", " + volt + ", R" + i
			ped = get_pedestal(file_name, int(i), preped, 'R'+str(13-int(i)),RFile_name,scale)
			#Locates the bad Channels
			#bad_chans = []
			#bad_chans = find_bad_chans(file_name, int(i)i, ped, 'R'+str(13-int(i)),RFile_name,scale)
			#Calculates Signal + Fits Landau/Gaussian

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
				
			get_signal(file_name, int(i), preped, 'R'+str(13-int(i)),RFile_name,bad_chans, runNum, scale, T_Array) # *****Try running off preped***** 
			if getEta == 1:
				file_name = folder+'Raw_Data_'+root_name+'_R'
				print file_name + i
        
				#if i+1<10: file_name += '0'
				file_name+=i+'.dat'
        
				#Generates Pedestal from Signal Data
				ped = []
				#2
				#ped = get_pedestal2(file_name,start_chan[i-1], end_chan[i-1], preped, 'R'+str(i)+'_'+volt+'_'+mat+'irr_'+temp+'C',RFile_name,scale)
				ped = get_pedestal2(file_name,start_chan[0], end_chan[0], preped, 'R'+str(i)+'_'+volt+'_'+mat+'_'+temp+'C',RFile_name,scale)
        
				CMsubtracted_noise = get_CMNoi(preped_name, preped, CMreg, ped[1], title, RFile_name, 1)


				#3
				#max_hit = get_signalDoubleMetal_CountMax(file_name, start_chan[0], end_chan[0], ped[0], CMreg, ped[1], CMsubtracted_noise,  'R'+str(i)+'_'+volt+'_'+mat+'irr_'+temp+'C', RFile_name,dd[0], scale, start=10)
				#get_signalDoubleMetal_Eta(file_name, start_chan[0], end_chan[0], ped[0], CMreg, ped[1], CMsubtracted_noise,  'R'+str(i)+'_'+volt+'_'+mat+'irr_'+temp+'C', RFile_name, max_hit, dd[0], scale, start=10)
				get_signalDoubleMetal_strip(file_name, start_chan[-1], end_chan[0], ped[0], CMreg, ped[1], CMsubtracted_noise,  'R'+str(i)+'_'+volt+'_'+mat+'_'+temp+'C', RFile_name,  dd[0], scale, start=10)


RStrip_Name = filePrefix + '_StripInfo.root'
RStripFile = R.TFile(RStrip_Name,'RECREATE')
RTree.Write()
RStripFile.Close()

