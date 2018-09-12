import ROOT as R
from Methods import *
import time
import os.path

R.gROOT.ProcessLine('.L Code/LandauFit.C+')

#filePrefix = sys.argv[1]    #ex: FTH200P_LTR10
#folder = sys.argv[2]	#Where data files are stored. ex: '/home/dtersegno/Raw_Data/LongTerm/FTH200P_R10/'
runMinstr = sys.argv[1]    #The minimum and maximum run numbers tolook at.
runMaxstr = sys.argv[2]
runinfo = sys.argv[3]
runMin = int(runMinstr)
runMax = int(runMaxstr)

#Get Run information from currentruninfo.txt
f = open(runinfo,"r")
filePrefix = f.readline()[:-1]
datafolder = f.readline()[:-1]
rootfolder = f.readline()[:-1]
regline = f.readline()[:-1]
regions = regline.split(' ')
vline = f.readline()[:-1]
Volts = vline.split(' ')
print filePrefix, datafolder, rootfolder, regions, Volts
f.close()

#scale allows for conversion of ADC counts to another value. The 192k value is ~num electrons.
#scale = 192000/255
scale = 1

runno = array('i',[0])
rgn = array('i',[0])
strip = array('i',[0])
badch = array('i',[0])
ppd = array('f',[0.])
pnoise = array('f',[0.])
pd = array('f',[0.])
noise = array('f',[0.])
src = array('f',[0.])
time = array('f',[0.])
TChuck = array('f',[0.])

c1 = R.TCanvas( 'c1', 'Strip Information', 200, 10, 700, 900)
c1.Divide(2,2)
c2 = R.TCanvas( 'c2', 'Strip Info vs Time', 200, 10, 700, 900)
c2.Divide(1,4)

RTree = R.TTree('strips','Strip Info')
RTree.Branch('run',runno,'runno/I')
RTree.Branch('rgn',rgn,'rgn/I')
RTree.Branch('strip',strip,'strip/I')
RTree.Branch('badch',badch,'badch/I')
RTree.Branch('ppd',ppd,'ppd/F')
RTree.Branch('pnoise',pnoise,'pnoise/F')
RTree.Branch('pd',pd,'pd/F')
RTree.Branch('noise',noise,'noise/F')
RTree.Branch('src',src,'src/F')
RTree.Branch('time',time,'time/F')
RTree.Branch('TChuck',TChuck,'TChuck/F')


TFile_name = datafolder + filePrefix + '_Env.dat'
T_Array = get_tempdata(TFile_name, rootfolder, filePrefix)

tmlo = 999999999999
ppdlo = pedlo = pnslo = nslo = 256
ppdhi = pedhi = pnshi = nshi = tmhi = 0		

for runNum in range(runMin,runMax+1):
	print "Processing run number: ", runNum
	for volt in reversed(Volts):

		root_name = filePrefix + "_" + str(runNum)
		RFile_name = rootfolder + filePrefix + "_" + str(runNum) + ".root"
		if not os.path.isfile(RFile_name):
			root_name = filePrefix + "_T" + str(runNum)
			RFile_name = rootfolder + filePrefix + "_T" + str(runNum) + ".root"
		RPedFile = R.TFile(RFile_name, 'READ')
		preped = RPedFile.Get("Ped Data PrePed")
		#Generates the Pre-Pedestal
		#print "Prepedestal for " + root_name +", " + volt
		#preped_name = datafolder + 'Raw_Data_'+root_name + '_Ped.dat'
		#preped_name = datafolder + root_name + '_Ped.dat'
		#preped = get_preped(preped_name, 'PrePed', RFile_name, 1)

		for i in regions:
			ped = RPedFile.Get("Ped Data R" + str(int(i)))
			file_name = datafolder + root_name + "_Ped.dat"
			#print "File", file_name, str(int(i))
			sr_hname = "R"+str(int(i))+" Data"
			srhits = RPedFile.Get(sr_hname)
			#bad_chans = find_bad_chans(file_name, int(i), preped, 'R'+str(int(i)),RFile_name,scale)			
			#Fill Tree of Strip Information
			for x in xrange(32):
				y = 32*(int(i)+1)+x
				runno[0] = runNum
				rgn[0] = int(i)
				strip[0] = x
				tmstamp = RPedFile.Get("PedStartTime")[0]
				TChuck[0] = get_temp(T_Array, tmstamp)[0]
				time[0] = tmstamp/(60*60*24)-40500
				badch[0] = 0
				#if x in bad_chans:  badch[0] = 1
				ppd[0] = preped.GetBinContent(y+1)
				pnoise[0] = preped.GetBinError(y+1)*R.sqrt(preped.GetBinEntries(y+1))
				pd[0] = ped.GetBinContent(y+1)
				noise[0] = ped.GetBinError(y+1)*R.sqrt(preped.GetBinEntries(y+1))
				src[0] = srhits.GetBinContent(x+1)
				#print 'preped', x, preped.GetBinContent(y+1),preped.GetBinError(y+1)*R.sqrt(ped.GetBinEntries(y+1)), preped.GetBinEntries(y+1)
				#print 'ped   ', x, ped.GetBinContent(y+1),ped.GetBinError(y+1)*R.sqrt(ped.GetBinEntries(y+1)), ped.GetBinEntries(y+1)
				RTree.Fill()
				if pd[0] < pedlo:  pedlo = pd[0]
				if ppd[0] < ppdlo:  ppdlo = ppd[0]
				if pd[0] > pedhi:  pedhi = pd[0]
				if ppd[0] > ppdhi:  ppdhi = ppd[0]
				if noise[0] < nslo:  nslo = noise[0]
				if pnoise[0] < pnslo:  pnslo = pnoise[0]
				if noise[0] > nshi:  nshi = noise[0]
				if pnoise[0] > pnshi:  pnshi = pnoise[0]
				if time[0] < tmlo: tmlo = time[0]
				if time[0] > tmhi: tmhi = time[0]
				

print pedlo,pedhi,ppdlo,ppdhi,nslo,nshi,pnslo,pnshi
RStrip_Name = rootfolder + "_" + filePrefix + '_Summary.root'
if os.path.isfile(RStrip_Name):  RStripFile = R.TFile(RStrip_Name,'UPDATE')
else:  RStripFile = R.TFile(RStrip_Name,'CREATE')

#hpns_stp = R.TH2F("hpns_stp","Preped Noise by Strip (all Runs)",32,0,32,32,pnslo,pnshi)
#hns_stp = R.TH2F("hns_stp","Noise by Strip (all Runs)",32,0,32,32,nslo,nshi)
#hppd_stp = R.TH2F("hppd_stp","PrePedestal by Strip (all Runs)",32,0,32,32,ppdlo,ppdhi)
#hpd_stp = R.TH2F("hpd_stp","Pedestal by Strip (all Runs)",32,0,32,32,pedlo,pedhi)
#hpns_tm = R.TH2F("hpns_tm","Preped Noise vs Run #",(runMax-runMin+1),runMin,runMax,32,pnslo,pnshi)
#hns_tm = R.TH2F("hns_tm","Noise vs Run #",(runMax-runMin+1),runMin,runMax,32,nslo,nshi)
#hppd_tm = R.TH2F("hppd_tm","PrePedestal vs Run #",(runMax-runMin+1),runMin,runMax,32,ppdlo,ppdhi)
#hpd_tm = R.TH2F("hpd_tm","Pedestal vs Run #",(runMax-runMin+1),runMin,runMax,32,pedlo,pedhi)
hpns_stp = R.TProfile("hpns_stp","Preped Noise by Strip (all Runs)",32,0,32)
hns_stp = R.TProfile("hns_stp","Noise by Strip (all Runs)",32,0,32)
hppd_stp = R.TProfile("hppd_stp","PrePedestal by Strip (all Runs)",32,0,32)
hpd_stp = R.TProfile("hpd_stp","Pedestal by Strip (all Runs)",32,0,32)
hpns_tm = R.TProfile("hpns_tm","Preped Noise vs Run #",(runMax-runMin+1),runMin,runMax)
hns_tm = R.TProfile("hns_tm","Noise vs Run #",(runMax-runMin+1),runMin,runMax)
hppd_tm = R.TProfile("hppd_tm","PrePedestal vs Run #",(runMax-runMin+1),runMin,runMax)
hpd_tm = R.TProfile("hpd_tm","Pedestal vs Run #",(runMax-runMin+1),runMin,runMax)
hpns_stp.GetXaxis().SetTitle("Strip Number")
hpns_stp.GetYaxis().SetTitle("Preped Noise")
hns_stp.GetXaxis().SetTitle("Strip Number")
hns_stp.GetYaxis().SetTitle("Ped Noise")
hppd_stp.GetXaxis().SetTitle("Strip Number")
hppd_stp.GetYaxis().SetTitle("Prepedestal")
hpd_stp.GetXaxis().SetTitle("Strip Number")
hpd_stp.GetYaxis().SetTitle("Pedestal")
hpns_tm.GetXaxis().SetTitle("Time (Days)")
hpns_tm.GetYaxis().SetTitle("Preped Noise")
hns_tm.GetXaxis().SetTitle("Time (Days)")
hns_tm.GetYaxis().SetTitle("Ped Noise")
hppd_tm.GetXaxis().SetTitle("Time (Days)")
hppd_tm.GetYaxis().SetTitle("Prepedestal")
hpd_tm.GetXaxis().SetTitle("Time (Days)")
hpd_tm.GetYaxis().SetTitle("Pedestal")

#hpns_stp.SetOption("colz")
#hns_stp.SetOption("colz")
#hppd_stp.SetOption("colz")
#hpd_stp.SetOption("colz")
#hpns_tm.SetOption("colz")
#hns_tm.SetOption("colz")
#hppd_tm.SetOption("colz")
#hpd_tm.SetOption("colz")

RTree.GetPlayer().SetScanRedirect(R.TObject.kTRUE) # You may have to cast t.GetPlayer() to a TTreePlayer*
RTree.GetPlayer().SetScanFileName(filePrefix+".txt")
RTree.Scan("*")
RTree.Write("",R.TObject.kOverwrite)
c1.cd(1)
RTree.Draw("ppd:strip>>hppd_stp","","colz")
c1.cd(2)
RTree.Draw("pnoise:strip>>hpns_stp","","colz")
c1.cd(3)
RTree.Draw("pd:strip>>hpd_stp","","colz")
c1.cd(4)
RTree.Draw("noise:strip>>hns_stp","","colz")
c1.SaveAs(rootfolder+filePrefix+"_StripInfo.jpg")
c2.cd(1)
RTree.Draw("ppd:runno>>hppd_tm","","colz")
c2.cd(2)
RTree.Draw("pnoise:runno>>hpns_tm","","colz")
c2.cd(3)
RTree.Draw("pd:runno>>hpd_tm","","colz")
c2.cd(4)
RTree.Draw("noise:runno>>hns_tm","","colz")
c2.SaveAs(rootfolder+filePrefix+"_StrInfovt.jpg")
#hpns_stp.Write("",R.TObject.kOverwrite)
#hns_stp.Write("",R.TObject.kOverwrite)
#hppd_stp.Write("",R.TObject.kOverwrite)
#hpd_stp.Write("",R.TObject.kOverwrite)
#hpns_tm.Write("",R.TObject.kOverwrite)
#hns_tm.Write("",R.TObject.kOverwrite)
#hppd_tm.Write("",R.TObject.kOverwrite)
#hpd_tm.Write("",R.TObject.kOverwrite)
RStripFile.Write("",R.TObject.kOverwrite)
RStripFile.Close()

