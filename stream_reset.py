import ROOT as R
from Methods import *
import time

runstart = sys.argv[1]
runend = sys.argv[2]
runinfo = sys.argv[3]    #ex: FTH200P_LTR10
#folder = sys.argv[2]	#Where data files are stored. ex: '/home/dtersegno/Raw_Data/LongTerm/FTH200P_R10/'

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
#f = open("currentruninfo.txt","r")
f = open(runinfo,"r")
filePrefix = f.readline()[:-1]
folder = f.readline()[:-1]
outfolder = f.readline()[:-1]
regline = f.readline()[:-1]
regions = regline.split(' ')
vline = f.readline()[:-1]
Volts = vline.split(' ')
print filePrefix, folder, regions
f.close()

TFile_name = folder + filePrefix + '_Env.dat'
T_Array = get_tempdata(TFile_name, outfolder, filePrefix)

#Find bad/noisy channels from calibration
#bad_chans = cal_sensor("FTH200Y_lat4_Cal")
#print bad_chans
bad_chans = [95,159,193]

runnum = 0
k = 0
scale = 1

print filePrefix + "_"+str(runnum)+"_0_Ped.dat"

while os.path.isfile(folder+filePrefix+"_"+str(runnum)+"_0_Ped.dat"):
        j = 0
	while os.path.isfile(folder+filePrefix+"_"+str(runnum)+"_" + str(j) + "_Ped.dat"):

		#Only run over selected files
		#print runstart, runend, k, j
		if ((k < int(runstart)) or (k > int(runend))):
			k+=1
			j+=1
			continue

		root_name = filePrefix + "_" + str(k)
		#Creates Root File for each voltage to store Plots 
		RFile_name = outfolder + root_name + '.root'
		RFile = R.TFile(RFile_name, 'RECREATE')
		RFile.Close()
		print root_name

		for i in regions:
			#Generates the Pre-Pedestal
			print "Prepedestal for " + root_name
			preped_name = folder + filePrefix + "_" + str(runnum) + "_" + str(j) + '_Ped.dat'
			if not os.path.isfile(preped_name): preped_name = folder + "Raw_Data_" + filePrefix + "_T" + str(runnum) + "_Ped.dat"
			preped = get_preped(preped_name, 'PrePed', int(i), RFile_name, 1)
			file_name = folder+ filePrefix + "_" + str(runnum) + "_" + str(j) +'_Sr90.dat'
			#file_name+=str(i)+'.dat'  
			#Generates Pedestal from Signal Data
			print "Pedestal for " + root_name +", " + ", R" + i
			ped = get_pedestal(file_name, int(i), preped, 'R'+str(13-int(i)),RFile_name,scale)
			#Locates the bad Channels
			#bad_chans = []
			#bad_chans = find_bad_chans(file_name, int(i)i, ped, 'R'+str(13-int(i)),RFile_name,scale)
			#Calculates Signal + Fits Landau/Gaussian

			#Fill Tree of Strip Information
			for x in xrange(32):
				y = 32*(int(i)+1)+x
				runno[0] = k
				rgn[0] = int(i)
				strip[0] = y
				badch[0] = 0
				#if x in bad_chans:  badch[0] = 1
				pd[0] = preped.GetBinContent(y+1) #Was running off ped instead of preped
				noise[0] = preped.GetBinError(y+1)*R.sqrt(preped.GetBinEntries(y+1))
				#print 'preped', x, preped.GetBinContent(y+1),preped.GetBinError(y+1)*R.sqrt(ped.GetBinEntries(y+1)), preped.GetBinEntries(y+1)
				#print 'ped   ', x, ped.GetBinContent(y+1),ped.GetBinError(y+1)*R.sqrt(ped.GetBinEntries(y+1)), ped.GetBinEntries(y+1)
				RTree.Fill()
				
			get_signal(file_name, int(i), preped, 'R'+str(13-int(i)),RFile_name,bad_chans, k, scale, T_Array) # *****Try running off preped***** 

		j += 1
		k += 1
        runnum += 1

RStrip_Name = filePrefix + '_StripInfo.root'
RStripFile = R.TFile(RStrip_Name,'RECREATE')
RTree.Write()
RStripFile.Close()

