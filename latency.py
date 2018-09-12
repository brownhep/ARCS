import ROOT as R
from Methods import *
import time

#filePrefix = sys.argv[1]    #ex: FTH200P_LTR10
#folder = sys.argv[2]	#Where data files are stored. ex: '/home/dtersegno/Raw_Data/LongTerm/FTH200P_R10/'
#runMin = sys.argv[1]    #The minimum and maximum run numbers tolook at.
#runMax = sys.argv[2]

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


Volts = [
	#'50V',
	#'75V',
	#'100V',
	#'125V',
	'150V',
	#'175V',
	#'200V',
	#'225V',
	#'250V',
	#'275V',
	#'300V',
	#'400V',
	#'450V',
	#'500V',
	#'525V',
	#'550V',
	#'575V',
	#'600V',
	#'650V',
	#'700V',
	#'750V',
	#'800V',
	#'900V',
	#'1000V',
	 ]
	 
regions = [
	#1,
	#2,
	#3,
	#4,
	#5,
	#6,
	#7,
	8,
	#9,
	#10,
	#11,
	#12
   ]

#Get Run information from currentruninfo.txt
f = open("currentruninfo.txt","r")
filePrefix = f.readline()[:-1]
folder = f.readline()[:-1]
outfolder = f.readline()[:-1]
print filePrefix, folder
f.close()

TFile_name = folder + filePrefix + '_Env.dat'
T_Array = get_tempdata(TFile_name, outfolder, filePrefix)

for runNum in range(int(runMin),int(runMax)+1):
	for volt in reversed(Volts):

		root_name = filePrefix + "_" + str(runNum)
		#Creates Root File for each voltage to store Plots 
		RFile_name = outfolder + root_name + '.root'
		RFile = R.TFile(RFile_name, 'RECREATE')
		RFile.Close()


		
		#Generates the Pre-Pedestal
		print "Prepedestal for " + root_name +", " + volt
		#preped_name = folder + 'Raw_Data_'+root_name + '_Lat.dat'
		preped_name = folder + root_name + '_Ped.dat'
		preped = get_preped(preped_name, 'PrePed', RFile_name, 1)

		for i in regions:
			file_name = folder+root_name+'_Lat.dat'
			#file_name = folder+'Raw_Data_'+root_name+'_Sr90.dat'
			#file_name+=str(i)+'.dat'  
			#Generates Pedestal from Signal Data
			print "Pedestal for " + root_name +", " + volt + ", R" + str(i)
			ped = get_pedestal(file_name, i, preped, 'R'+str(13-(i)),RFile_name,scale)

			#Fill Tree of Strip Information
			for x in xrange(32):
				y = 32*(i+1)+x
				runno[0] = runNum
				rgn[0] = i
				strip[0] = y
				badch[0] = 0
				#if x in bad_chans:  badch[0] = 1
				pd[0] = ped.GetBinContent(y+1) #Was running off ped instead of preped
				noise[0] = ped.GetBinError(y+1)*R.sqrt(ped.GetBinEntries(y+1))
				#print 'preped', x, preped.GetBinContent(y+1),preped.GetBinError(y+1)*R.sqrt(ped.GetBinEntries(y+1)), preped.GetBinEntries(y+1)
				#print 'ped   ', x, ped.GetBinContent(y+1),ped.GetBinError(y+1)*R.sqrt(ped.GetBinEntries(y+1)), ped.GetBinEntries(y+1)
				RTree.Fill()
				

RStrip_Name = filePrefix + '_StripInfo.root'
RStripFile = R.TFile(RStrip_Name,'RECREATE')
RTree.Write()
RStripFile.Close()

