import ROOT as R
from Methods import *
import time
import os.path

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
bad_chans = []

for runNum in range(int(runMin),int(runMax)+1):
	for volt in reversed(Volts):

		for i in regions:
			#if os.path.isfile(outfolder+filePrefix+"_T"+str(runNum)+".root"): root_name = filePrefix + "_T" + str(runNum)
                	#else: root_name = filePrefix + "_" + str(runNum)
                	root_name = filePrefix + "_" + str(runNum)
                	RFile_name = outfolder + filePrefix + "_" + str(runNum) + ".root"
                        file_name = folder+root_name+'_Sr90.dat'
                	if os.path.isfile(folder+"Raw_Data_"+filePrefix+"_T"+str(runNum)+'_R' + i + '.dat'):
                        	#root_name = filePrefix + "_T" + str(runNum)
                        	#RFile_name = outfolder + filePrefix + "_T" + str(runNum) + ".root"
				file_name = folder+"Raw_Data_"+filePrefix+"_T"+str(runNum)+'_R' + i + '.dat'
			print RFile_name, file_name
                	RPedFile = R.TFile(RFile_name, 'READ')
                	preped = RPedFile.Get("Ped Data PrePed")
                	ped = RPedFile.Get("Ped Data R" + str(13-int(i)))
			preped.Draw()
			#Locates the bad Channels
			#bad_chans = []
			#bad_chans = find_bad_chans(file_name, int(i)i, ped, 'R'+str(13-int(i)),RFile_name,scale)
			#Calculates Signal + Fits Landau/Gaussian

        		#RFileName = outfolder + filePrefix + "_hd.root"
        		#print RFileName
        		#rootfile = R.TFile(RFileName, "r")
        		#hdTree = rootfile.Get("hits")
        		#hdTree.Draw("hit_strip>>hhits2")
        		#hhits = R.gPad.GetPrimitive("hhits2")
        		#hhits.Fit("gaus")
        		#f1 = hhits.GetFunction("gaus")
        		#p0 = f1.GetParameter(0)
        		#mean = f1.GetParameter(1)
        		#sigma = f1.GetParameter(2)
        		#chi2 = f1.GetChisquare()
        		#print p0, mean, sigma, chi2
			#stripstart = int(round(mean - 3*sigma) - 1)
			#if stripstart < 0: stripstart = 0
			#stripend = int(round(mean + 3*sigma) + 1)
			#if stripend > 31: stripend = 31
			#print "Only take Data from strips between ", stripstart, stripend				
			stripstart = 0
			stripend = 31
			get_signal3(file_name, int(i), preped, 'R'+str(13-int(i)),RFile_name,bad_chans, runNum, scale, T_Array,stripstart,stripend) # *****Try running off preped***** 


