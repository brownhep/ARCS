import ROOT as R
import sys
import os.path
from array import array

#infolder = "./rootfiles/" #where the root files are. a folder that contains nonclus/----.root and clus/----.root
#outfolder = "./" #where to place the output
#runmin = 0 #minimum run to check.
runmin = sys.argv[1]
runmax = sys.argv[2] #maximum run to check
runinfo = sys.argv[3]

runmin = int(runmin)
runmax = int(runmax)

#Get Run information from currentruninfo.txt
f = open(runinfo,"r")
prefix = f.readline()[:-1]
rawdata = f.readline()[:-1]
infolder = f.readline()[:-1]
regline = f.readline()[:-1]
regions = regline.split(' ')
outfolder = infolder
#print prefix, folder, regions
f.close()

tm = array('f',[ 0. ])
temp = array('f',[ 0. ])
mp = array('f',[ 0. ])
mpe = array('f',[ 0. ])
chi2 = array('f',[ 0. ])
md_c = array('f',[ 0. ])
mde_c = array('f',[ 0. ])
md_s = array('f',[ 0. ])
mde_s = array('f',[ 0. ])
etapct = array('f',[ 0. ])

c1 = R.TCanvas( 'c1', 'Charge Collected vs Time', 200, 10, 800, 1000 )
c1.SetTitle(prefix+"_qvt")
c1.Divide(2,2)

c2 = R.TCanvas( 'Eta', 'Eta vs Time', 200, 10, 800, 1000 )
c2.SetTitle(prefix+"_eta")

RFile_Name = 'LTR_Summary.root'
RTree = R.TTree('ltr','LTRMeas')
RTree.Branch('time',tm,'time/F')
RTree.Branch('temp',temp,'temp/F')
RTree.Branch('MPV',mp,'MPV/F')
RTree.Branch('MPVerr',mpe,'MPVerr/F')
RTree.Branch('Chi2',chi2,'chi2/F')
RTree.Branch('med_clust',md_c,'med_clust/F')
RTree.Branch('mderr_clust',mde_c,'mderr_clust/F')
RTree.Branch('med_seed',md_s,'med_seed/F')
RTree.Branch('mderr_seed',mde_s,'mderr_seed/F')
RTree.Branch('etapct',etapct,'etapct/F')


fc = [] #creating a list of clustered root files to access

hhits = R.TH1I("hhits","Hit Distribution by Strip",32,0,32)
hhits2 = R.TH1I("hhits2","Hit Distribution by Strip",32,0,32)
MPVs = []
MPVgraph = R.TGraphErrors(runmax-runmin+1-6)
median = []
median_c = []
medgraph = R.TGraphErrors(runmax-runmin+1-6)
medgraph_c = R.TGraphErrors(runmax-runmin+1-6)
etagraph = R.TGraphErrors(runmax-runmin+1-6)
softevts = []
softgraph = R.TGraph(runmax-runmin+1-6)
noisyevts = []
noisygraph = R.TGraph(runmax-runmin+1-6)
pednsyevts = []
pednsygraph = R.TGraph(runmax-runmin+1-6)

for trial in range(runmin , runmax+1):
	RFile_name = infolder+prefix+"_"+str(trial)+".root"
	if not os.path.isfile(RFile_name):
		RFile_name = infolder+prefix+"_T"+str(trial)+".root"
	if trial > 241 and trial < 248: continue
    	fc.append(R.TFile(RFile_name))
    	print RFile_name

for r in regions:
    region = 13 - int(r)
    rootfile = R.TFile()

    i = 0
    t0 = 0
    for trial in range(runmin, runmax+1):
	#i = trial
	if trial > 241 and trial < 248:
		print "skipping run # ", trial
		#MPVs.append(0)
		#median.append(0)
		#median_c.append(0)
		continue
        #Getting MPV and time values from ROOT file
        print "Writing MPV value for trial "+str(trial)
        #print fc[trial], "R"+str(region)+"_MPV"
        tm[0]=fc[i].Get("StartTime")[0]
	#Setting start of run to be t = 0 days
	if t0 == 0: t0 = tm[0]
	tm[0] = tm[0] - t0
	temp[0] = fc[i].Get("StartTemp")[0]
        #tm[0]=(float(trial))
        MPVs.append(fc[i].Get("R"+str(region)+"_MPV")[0])
        MPVgraph.SetPoint(i,tm[0],MPVs[i])
        #MPVgraph.SetPoint(trial,trial,MPVs[trial])
        MPVgraph.SetPointError(i,0,.1)
        mp[0]=fc[i].Get("R"+str(region)+"_MPV")[0]
	chi2[0] = fc[i].Get("Chi2")[0]
        mpe[0]=0.1
	softgraph.SetPoint(i,tm[0],fc[i].Get("SoftEvents")[0])
	noisygraph.SetPoint(i,tm[0],fc[i].Get("NoisyEvents")[0])
	pednsygraph.SetPoint(i,tm[0],fc[i].Get("PedNoisyEvts")[0])
        print "Done writing values for trial "+str(trial)

        #Getting clustered Median values from ROOT file
        hist_name = 'R'+str(region)+' Signal_1000Bins_clust'
        print hist_name, fc[i]
        h = fc[i].Get(hist_name)
        hentries = h.GetEntries()
        counter = 0
        ticker = 0
        median_c.append(0)
        meanerror = h.GetMeanError()
        #print trial, median
        while median_c[i] == 0:
            counter += h[ticker]
            if counter >= hentries/2:
                median_c[i] = ((ticker + 0.5)/10)
            ticker += 1
        print "The T" + str(trial) + " cluster median is " + str(median_c[i])
	if trial == 243:
        	medgraph_c.SetPoint(i,tm[0],median_c[i-1])
	else:
        	medgraph_c.SetPoint(i,tm[0],median_c[i])
        medgraph_c.SetPointError(i,0,1.2*meanerror)
        md_c[0]=median_c[i]
        mde_c[0]=meanerror

        #Getting seed Median values from ROOT file
        hist_name = 'R'+str(region)+' Signal_1000Bins'
        print hist_name, fc[i]
        h = fc[i].Get(hist_name)
        hentries = h.GetEntries()
        counter = 0
        ticker = 0
        median.append(0)
        meanerror = h.GetMeanError()
        #print trial, median
        while median[i] == 0:
            counter += h[ticker]
            if counter >= hentries/2:
                median[i] = ((ticker + 0.5)/10)
            ticker += 1
        print "The T" + str(trial) + " median is " + str(median[i])
	if trial == 243:
        	medgraph.SetPoint(i,tm[0],median[i])
	else:
        	medgraph.SetPoint(i,tm[0],median[i])
        medgraph.SetPointError(i,0,1.2*meanerror)
        md_s[0]=median[i]
        mde_s[0]=meanerror

        #print "tree", tm, mp, mpe, md, mde
        RTree.Fill()

	c2.Print(outfolder+prefix+".ps[")

	if trial == 243:
		hEta = fc[i-1].Get("Eta")
	else:
		hEta = fc[i].Get("Eta")
	etapct[0] = hEta.Integral(30,89)/hEta.Integral()
	etagraph.SetPoint(i,tm[0],etapct[0])
	if i%40 == 0:
		hEta.SetLineColor(i/40 + 1)
		hEta.SetOption("L")
		normC = hEta.Integral()
		print "Integral value: ", normC
		hEta.Scale(1/normC)
		if i==0: hEta.Draw("L")
		else: hEta.Draw("Lsame")
		c2.Update()
		c2.SaveAs(outfolder+prefix+"_eta"+str(trial)+".jpg")
		c2.Print(outfolder+prefix+".ps")
	c2.Print(outfolder+prefix+".ps]")
        i += 1

	

if os.path.isfile(outfolder+"_"+prefix+"_Summary.root"): RFile = R.TFile(outfolder+"_"+prefix+"_Summary.root",'UPDATE')
else: RFile = R.TFile(outfolder+"_"+prefix+"_Summary.root",'RECREATE')
c2.Write("",R.TObject.kOverwrite)
RTree.Write("",R.TObject.kOverwrite)
MPVgraph.SetName(prefix+"_MPV")
MPVgraph.SetTitle("MPV vs Time")
MPVgraph.GetXaxis().SetTitle("Days")
MPVgraph.GetYaxis().SetTitle("ADC Counts")
MPVgraph.Write("",R.TObject.kOverwrite)
c1.cd(1)
MPVgraph.Draw()
c1.Update()
#c1.SaveAs(outfolder+prefix+"_MPV.jpg")
medgraph_c.SetName(prefix+"_Median_cluster")
medgraph_c.SetTitle("Cluster Median vs Time")
medgraph_c.GetXaxis().SetTitle("Days")
medgraph_c.GetYaxis().SetTitle("ADC Counts")
medgraph_c.Write("",R.TObject.kOverwrite)
c1.cd(2)
medgraph_c.Draw()
c1.Update()
#c1.SaveAs(outfolder+prefix+"_med_clust.jpg")
medgraph.SetName(prefix+"_Median")
medgraph.SetTitle("Seed Median vs Time")
medgraph.GetXaxis().SetTitle("Days")
medgraph.GetYaxis().SetTitle("ADC Counts")
medgraph.Write("",R.TObject.kOverwrite)
c1.cd(3)
medgraph.Draw()
c1.Update()
#c1.SaveAs(outfolder+prefix+"_med_seed.jpg")
c1.cd(4)
medgraph.SetTitle("Median vs Time")
medgraph.Draw()
#color = R.TColor(1)
medgraph_c.SetLineColor(R.TColor.kRed)
medgraph_c.Draw("same")
c1.Update()
c1.SaveAs(outfolder+prefix+"_qvt.jpg")
c1.Print(outfolder+prefix+"2.ps")
softgraph.SetMarkerStyle(3)
softgraph.SetName(prefix+"_softevts")
softgraph.SetTitle("Soft Events vs Time")
softgraph.GetXaxis().SetTitle("Days")
softgraph.GetYaxis().SetTitle("# Soft Events")
#softgraph.Draw("P")
softgraph.Write("",R.TObject.kOverwrite)
noisygraph.SetMarkerStyle(3)
noisygraph.SetName(prefix+"_nsyevts")
noisygraph.SetTitle("Noisy Events vs Time")
noisygraph.GetXaxis().SetTitle("Days")
noisygraph.GetYaxis().SetTitle("# Noisy Events")
noisygraph.Write("",R.TObject.kOverwrite)
pednsygraph.SetMarkerStyle(3)
pednsygraph.SetName(prefix+"_pednsyevts")
pednsygraph.SetTitle("Preped Noisy Events vs Time")
pednsygraph.GetXaxis().SetTitle("Days")
pednsygraph.GetYaxis().SetTitle("# Preped Noisy Events")
pednsygraph.Write("",R.TObject.kOverwrite)
etagraph.SetMarkerStyle(3)
etagraph.SetName(prefix+"_Eta%")
etagraph.SetTitle("Eta % .2-.8 vs Time")
etagraph.GetXaxis().SetTitle("Days")
etagraph.GetYaxis().SetTitle("Percent")
etagraph.Write("",R.TObject.kOverwrite)

RFile.Close()

