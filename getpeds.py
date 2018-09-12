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
                	root_name = filePrefix + "_" + str(runNum)
                	RFile_name = rootfolder + filePrefix + "_" + str(runNum) + ".root"
                	if not os.path.isfile(RFile_name):
                        	root_name = filePrefix + "_T" + str(runNum)
                        	RFile_name = rootfolder + filePrefix + "_T" + str(runNum) + ".root"
                	RPedFile = R.TFile(RFile_name, 'READ')
                	preped = RPedFile.Get("Ped Data PrePed")
			#Generates the Pre-Pedestal
			print "Prepedestal for " + root_name +", " + volt
			#preped_name = folder + 'Raw_Data_'+root_name + '_Ped.dat'
			preped_name = folder + root_name + '_Ped.dat'
			preped = get_preped(preped_name, 'PrePed', int(i), RFile_name, 1)
			file_name = folder+root_name+'_Sr90.dat'
			#file_name = folder+'Raw_Data_'+root_name+'_Sr90.dat'
			#file_name+=str(i)+'.dat'  
			#Generates Pedestal from Signal Data
			print "Pedestal for " + root_name +", " + volt + ", R" + i
			ped = get_pedestal(file_name, int(i), preped, 'R'+str(13-int(i)),RFile_name,scale)

