import ROOT as R
import sys
import os.path
from array import array

runinfo = sys.argv[1]

#Get Run information from currentruninfo.txt
f = open(runinfo,"r")
prefix = f.readline()[:-1]
rawdata = f.readline()[:-1]
infolder = f.readline()[:-1]
regline = f.readline()[:-1]
regions = regline.split(' ')
vline = f.readline()[:-1]
volts = regline.split(' ')
runmin = int(f.readline()[:-1])
runmax = int(f.readline()[:-1])
numruns = runmax - runmin + 1
outfolder = infolder
#print prefix, folder, regions
f.close()

hhits = R.TH1I("hhits0","Hit Distribution",32,0,32)
hhits.SetDirectory(0)
hCM = R.TH1F("hCM0","Common Mode Noise",100,-5,5)
hCM2 = R.TH1F("hCM","Common Mode Noise",100,-5,5)
hCM.SetDirectory(0)
hCMvt = R.TH2F("hCMvt0","Common Mode Noise vs Run #",numruns,runmin,runmax+1,100,-5,5)
hCMvt2 = R.TH2F("hCMvt","Common Mode Noise vs Run #",numruns,runmin,runmax+1,100,-5,5)
hCMvt.SetDirectory(0)

p0 = R.TVectorF(1)
p1 = R.TVectorF(1)
p2 = R.TVectorF(1)
chi2 = R.TVectorF(1)

c1 = R.TCanvas( 'c1', 'Charge Collected vs Time', 200, 10, 800, 1000 )
c1.Divide(2,2)

for r in regions:
	region = 13 - int(r)
	RFileName = outfolder + prefix + "_hd.root"
	print RFileName
	rootfile = R.TFile(RFileName, "r")
	hdTree = rootfile.Get("hits")
	c1.cd(1)
	hhits2 = R.TH1I("hhits","Hit Distribution",32,0,32)
        hdTree.Draw("hit_strip>>hhits2")
	hhits = R.gPad.GetPrimitive("hhits2")
        hhits.Fit("gaus")
        f1 = hhits.GetFunction("gaus")
        p0[0] = f1.GetParameter(0)
        p1[0] = f1.GetParameter(1)
        p2[0] = f1.GetParameter(2)
        chi2[0] = f1.GetChisquare()
	print p0, p1, p2, chi2
	c1.cd(2)
        hdTree.Draw("CM_noise>>hCM2")
	hCM = R.gPad.GetPrimitive("hCM2")
	c1.cd(3) 
	hdTree.Draw("CM_noise:runno>>hCMvt2","","colz")
	hCMvt = R.gPad.GetPrimitive("hCMvt2")
	c1.cd(4)
	hhits.Draw()
	c1.Update()
	c1.SaveAs("test.jpg")



if os.path.isfile(outfolder+"_"+prefix+"_Summary.root"): RFile = R.TFile(outfolder+"_"+prefix+"_Summary.root",'UPDATE')
else: RFile = R.TFile(outfolder+"_"+prefix+"_Summary.root",'RECREATE')
hhits.GetXaxis().SetTitle("Strip Number")
hhits.Write("",R.TObject.kOverwrite)
hCM.GetXaxis().SetTitle("CM Noise")
hCM.Write("",R.TObject.kOverwrite)
hCMvt.GetXaxis().SetTitle("Time (Days)")
hCMvt.GetYaxis().SetTitle("CM Noise")
hCMvt.SetOption("colz")
hCMvt.Write("",R.TObject.kOverwrite)
p0.Write("gaus_p0",R.TObject.kOverwrite)
p1.Write("gaus_p1",R.TObject.kOverwrite)
p2.Write("gaus_p2",R.TObject.kOverwrite)
chi2.Write("gaus_chi2",R.TObject.kOverwrite)
