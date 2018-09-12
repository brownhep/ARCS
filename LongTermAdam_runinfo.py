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
biasv = f.readline()[:-1]
runMin = f.readline()[:-1]
runMax = f.readline()[:-1]
outfolder = infolder
#print prefix, folder, regions
f.close()

runmin = int(runMin)
runmax = int(runMax)


fc = {} #creating a list of clustered root files to access
fchd = {} #creating a list of hit data clustered root files to access
mergepdf = "#!/bin/tcsh\n"
mergepdf += "gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -sOutputFile=" + infolder + prefix + ".pdf"

####Account for missing run files
exclude_runs = []
##

for trial in range(runmin , runmax+1):
        mergepdf += " " + infolder + prefix + "_" + str(trial) + ".pdf"
	RFile_name = infolder+prefix+"_"+str(trial)+".root"
	RFile_namehd = infolder+prefix+"_"+str(trial)+"_hd.root"
	if trial in exclude_runs:
	    	fc[trial] = 0
	    	fchd[trial] = 0
		continue
	if not (os.path.isfile(RFile_name) and os.path.isfile(RFile_namehd)):
	    	fc[trial] = 0
	    	fchd[trial] = 0
		exclude_runs.append(trial)
		continue
#		RFile_name = infolder+prefix+"_T"+str(trial)+".root"
    	fc[trial] = R.TFile(RFile_name)
    	fchd[trial] = RFile_namehd

mergepdf += "\n"
for trial in range(runmin , runmax+1):
	mergepdf += "rm " + infolder + prefix + "_" + str(trial) + ".pdf\n"
mergefile = open("mergefile.csh", "w")
mergefile.write(mergepdf)
mergefile.close()

#The actual number of runs to be plotted
NRUNS = len(fc)-1


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


hhits = R.TH1I("hhits","Hit Distribution by Strip",32,0,32)
MPVs = []
MPVgraph = R.TGraphErrors(NRUNS)
median = []
median_c = []
medgraph = R.TGraphErrors(NRUNS)
medgraph_c = R.TGraphErrors(NRUNS)
etagraph = R.TGraphErrors(NRUNS)
softevts = []
softgraph = R.TGraph(NRUNS)
noisyevts = []
noisygraph = R.TGraph(NRUNS)
pednsyevts = []
pednsygraph = R.TGraph(NRUNS)
dmedgraph = R.TGraph(NRUNS - 3)
dmedcgraph = R.TGraph(NRUNS - 3)
detagraph = R.TGraph(NRUNS - 3)
timeary = []
etaary = []
chimax = 1
chimaxeta = 1
pmedmax = 0
pmedcmax = 0
petamax = 0

sumfile = open ("runsummary.txt", "a")
sumfile.write("Region " + ' '.join(regions) + "\n")
sumfile.close()


for r in regions:
    region = 13-int(r)
    rootfile = R.TFile()

    i = 0
    t0 = 0
    for trial in range(runmin, runmax):
	print fc[trial]
	if trial in exclude_runs:
		continue
	hhits2 = R.TH1I("hhits2","Hit Distribution by Strip",32,0,32)
	hdfile = R.TFile(fchd[trial])
	hdfile.Get("hits").Draw("hit_strip>>hhits2")
	hhits = R.gPad.GetPrimitive("hhits2")
	hhits.Fit("gaus")
	f1 = hhits.GetFunction("gaus")
	p0 = f1.GetParameter(0)
	p1 = f1.GetParameter(1)
	p2 = f1.GetParameter(2)
	hits_chi2 = f1.GetChisquare()
	hdfile.Close()
        #Getting MPV and time values from ROOT file
        print "Writing MPV value for trial "+str(trial)
        #print fc[trial], "R"+str(region)+"_MPV"
        abstime=fc[trial].Get("StartTime")[0]
        starttemp=fc[trial].Get("StartTemp")[0]
	#Setting start of run to be t = 0 days
	if t0 == 0: t0 = abstime
	tm[0] = abstime - t0
	print "time ", trial, tm[0]
	timeary.append(tm[0])
	#print "appending ", tm[0], timeary
	temp[0] = fc[trial].Get("StartTemp")[0]
        #tm[0]=(float(trial))
        MPVs.append(fc[trial].Get("R"+str(region)+"_MPV")[0])
        MPVgraph.SetPoint(i,tm[0],MPVs[i])
        #MPVgraph.SetPoint(trial,trial,MPVs[trial])
        MPVgraph.SetPointError(i,0,.1)
        mp[0]=fc[trial].Get("R"+str(region)+"_MPV")[0]
	chi2[0] = fc[trial].Get("Chi2")[0]
        mpe[0]=0.1
	softgraph.SetPoint(i,tm[0],fc[trial].Get("SoftEvents")[0])
	noisygraph.SetPoint(i,tm[0],fc[trial].Get("NoisyEvents")[0])
#	pednsygraph.SetPoint(i,tm[0],fc[i].Get("PedNoisyEvts")[0])
        #print "Done writing values for trial "+str(trial)

        #Getting clustered Median values from ROOT file
        hist_name = 'R'+str(region)+' Signal_1000Bins_clust'
        #print hist_name, fc[i]
        h = fc[trial].Get(hist_name)
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
        medgraph_c.SetPoint(i,tm[0],median_c[i])
        medgraph_c.SetPointError(i,0,1.2*meanerror)
        md_c[0]=median_c[i]
        mde_c[0]=meanerror

        #Getting seed Median values from ROOT file
        hist_name = 'R'+str(region)+' Signal_1000Bins'
        #print hist_name, fc[i]
        h = fc[trial].Get(hist_name)
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
        medgraph.SetPoint(i,tm[0],median[i])
        medgraph.SetPointError(i,0,1.2*meanerror)
        md_s[0]=median[i]
        mde_s[0]=meanerror

        #print "tree", tm, mp, mpe, md, mde
        RTree.Fill()

	#c2.Print(outfolder+prefix+".ps[")

	hEta = fc[trial].Get("Eta")
	etapct[0] = hEta.Integral(30,89)/hEta.Integral()
	etaary.append(etapct[0])
	etagraph.SetPoint(i,tm[0],etapct[0])
	if i%40 == 0:
		hEta.SetLineColor(i/40 + 1)
		hEta.SetOption("L")
		normC = hEta.Integral()
		#print "Integral value: ", normC
		hEta.Scale(1/normC)
		if i==0: hEta.Draw()
		else: hEta.Draw("same")
		c2.Update()
		#c2.SaveAs(outfolder+prefix+"_eta"+str(trial)+".jpg")
		#c2.Print(outfolder+prefix+".ps")
	#c2.Print(outfolder+prefix+".ps]")

	if i > 3: #Enough to do linear fit of last 5 points
		meds5 = median[i-4:i+1]
		medc5 = median_c[i-4:i+1]
		eta5 = etaary[i-4:i+1]
		tm5 = timeary[i-4:i+1]
		print tm5, meds5, medc5
		med5grph = R.TGraph(5)
		medc5grph = R.TGraph(5)
		eta5grph = R.TGraph(5)
		for j in xrange(5):
			#print j
			med5grph.SetPoint(j, tm5[j], meds5[j])
			medc5grph.SetPoint(j, tm5[j], medc5[j])
			eta5grph.SetPoint(j, tm5[j], eta5[j])
		
		med5grph.Fit("pol1")
		fmed = med5grph.GetFunction("pol1")
		pmed = fmed.GetParameter(1)
		dmedgraph.SetPoint(i-4, tm5[2], pmed)
		chimed = fmed.GetChisquare()
		if (pmed < pmedmax) and (chimed < chimax):
			pmedmax = pmed
			print "Pmed max: ", i, pmedmax, chimed
			imedmax = tm5[2]
			chims = chimed
		medc5grph.Fit("pol1")
		fmedc = medc5grph.GetFunction("pol1")
		pmedc = fmedc.GetParameter(1)
		dmedcgraph.SetPoint(i-4, tm5[2], pmedc)
		chimedc = fmedc.GetChisquare()
		if (pmedc < pmedcmax) and (chimedc < chimax):
			pmedcmax = pmedc
			print "Pmedc max: ", i, pmedcmax, chimedc
			imedcmax = tm5[2]
			chimc = chimedc
		eta5grph.Fit("pol1")
		feta = eta5grph.GetFunction("pol1")
		peta = feta.GetParameter(1)
		detagraph.SetPoint(i-4, tm5[2], peta)
		chieta = feta.GetChisquare()
		if (peta > petamax) and (chieta < chimaxeta):
			petamax = peta
			print "Peta max: ", i, petamax, chieta
			ietamax = tm5[2]
			chie = chieta
	sumfile = open ("runsummary.txt", "a")
	sumfile.write (str(abstime)+"\t"+str(starttemp)+"\t"+str(mp[0])+"\t"+str(md_s[0])+"\t"+str(md_c[0])+"\t"+str(etapct[0])+"\t"+str(p1)+"\t"+str(p2)+"\n")        
	sumfile.close()

	fc[trial].Close()
	i += 1

#print "Seed Median Derivative (run #, Max): ", pmedmax, imedmax, chims
#print "Cluster Median Derivative (run #, Max): ", pmedcmax, imedcmax, chimc
#print "Eta Derivative (run #, Max): ", petamax, ietamax, chie
	

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
etagraph.SetTitle("Eta vs Time")
#medgraph.Draw()
#medgraph_c.SetLineColor(R.TColor.kRed)
#medgraph_c.Draw("same")
etagraph.Draw()
c1.Update()
#c1.SaveAs(outfolder+prefix+"_qvt.jpg")
c1.Print(outfolder+prefix+".pdf")
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
#pednsygraph.SetMarkerStyle(3)
#pednsygraph.SetName(prefix+"_pednsyevts")
#pednsygraph.SetTitle("Preped Noisy Events vs Time")
#pednsygraph.GetXaxis().SetTitle("Days")
#pednsygraph.GetYaxis().SetTitle("# Preped Noisy Events")
#pednsygraph.Write("",R.TObject.kOverwrite)
etagraph.SetMarkerStyle(3)
etagraph.SetName(prefix+"_Eta%")
etagraph.SetTitle("Eta % .2-.8 vs Time")
etagraph.GetXaxis().SetTitle("Days")
etagraph.GetYaxis().SetTitle("Percent")
etagraph.Write("",R.TObject.kOverwrite)
dmedgraph.Write("Seed_Med_Der",R.TObject.kOverwrite)
dmedcgraph.Write("Clust_Med_Der",R.TObject.kOverwrite)
detagraph.Write("Eta_Der",R.TObject.kOverwrite)
RFile.Close()

