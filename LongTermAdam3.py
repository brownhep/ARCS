import ROOT as R
import sys
import os.path
from array import array

#infolder = "./rootfiles/" #where the root files are. a folder that contains nonclus/----.root and clus/----.root
#outfolder = "./" #where to place the output
#runmin = 0 #minimum run to check.
#runmin = sys.argv[1]
#runmax = sys.argv[2] #maximum run to check
#runinfo = sys.argv[1]


#param_file = "/home/alanman/configs/unirr_R11_config"
#param_file = "/home/alanman/configs/unirr_R12_config"
#param_file = "/home/alanman/configs/unirr_R5_config"
#param_file = "/home/alanman/configs/unirr_R7_config"

param_file = "/home/espencer/FTH200N_config"


params = {}
with open (param_file) as f:
	for line in f:
		if line[:1] == "#" or len(line) == 0: continue
		try:
			(key, val) = [x.strip() for x in line.split(":")]
		except ValueError:
			pass
		if key == "regions" or key == "volts":
			val = val.split(" ")
		params[key] = val
		if key == "good_chans":
		   #Parse the line
			ls = []
			for s in val.split(" "):
			   s = s.strip()
			   if s[0] == "(":
				x = s[s.find("(")+1:s.find(")")].split(",")
				ls.extend(range(int(x[0]),int(x[1])))
			   else:
				ls.append(int(s))
			params[key] = ls
		key, val = "", ""

runMin = params['runMin']
runMax = params['runMax']

if "good_chans" in params:
    good_chans = params['good_chans']

if len(sys.argv) == 3:
	runMin = sys.argv[1]    #The minimum and maximum run numbers tolook at.
	runMax = sys.argv[2]

prefix = params['filePrefix']
rawdata = params['inFolder']
infolder = params['outFolder']
regions = params['regions']
biasv = params['volts'][0]
runmin = params['runMin']
runmax = params['runMax']
outfolder = infolder

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
mergefile = open("mergefile.csh", "w")
mergefile.write(mergepdf)
mergefile.close()

#The actual number of runs to be plotted
NRUNS = len(fc)-1


tm = array('f',[ 0. ])
temp = array('f',[ 0. ])
mp = array('f',3*[ 0. ])
mpe = array('f',3*[ 0. ])
chi2 = array('f',3*[ 0. ])
md_c = array('f',3*[ 0. ])
mde_c = array('f',3*[ 0. ])
md_s = array('f',3*[ 0. ])
mde_s = array('f',3*[ 0. ])
etapct = array('f',3*[ 0. ])

c1 = R.TCanvas( 'c1', 'Charge Collected vs Time', 200, 10, 800, 1000 )
c1.SetTitle(prefix+"_qvt")
c1.Divide(2,2)

c2 = R.TCanvas( 'Eta', 'Eta vs Time', 200, 10, 800, 1000 )
c2.SetTitle(prefix+"_eta")

RFile_Name = 'LTR_Summary.root'
RTree = R.TTree('ltr','LTRMeas')
RTree.Branch('time',tm,'time/F')
RTree.Branch('temp',temp,'temp/F')
RTree.Branch('MPV',mp,'MPV[3]/F')
RTree.Branch('MPVerr',mpe,'MPVerr[3]/F')
RTree.Branch('Chi2',chi2,'chi2[3]/F')
RTree.Branch('med_clust',md_c,'med_clust[3]/F')
RTree.Branch('mderr_clust',mde_c,'mderr_clust[3]/F')
RTree.Branch('med_seed',md_s,'med_seed[3]/F')
RTree.Branch('mderr_seed',mde_s,'mderr_seed[3]/F')
RTree.Branch('etapct',etapct,'etapct[3]/F')


hhits = R.TH1I("hhits","Hit Distribution by Strip",32,0,32)
MPVs = []
#MPVgraph = R.TGraphErrors(NRUNS)
MPVgraph0 = R.TGraphErrors(NRUNS)
MPVgraph1 = R.TGraphErrors(NRUNS)
MPVgraph2 = R.TGraphErrors(NRUNS)
median = []
median_c = []
medgraph = R.TGraphErrors(NRUNS)
medgraph0 = R.TGraphErrors(NRUNS)
medgraph1 = R.TGraphErrors(NRUNS)
medgraph2 = R.TGraphErrors(NRUNS)
medgraph_c = R.TGraphErrors(NRUNS)
medgraph_c0 = R.TGraphErrors(NRUNS)
medgraph_c1 = R.TGraphErrors(NRUNS)
medgraph_c2 = R.TGraphErrors(NRUNS)
etagraph0 = R.TGraphErrors(NRUNS)
etagraph1 = R.TGraphErrors(NRUNS)
etagraph2 = R.TGraphErrors(NRUNS)
softevts = []
softgraph = R.TGraph(NRUNS+1)
noisyevts = []
noisygraph = R.TGraph(NRUNS+1)
pednsyevts = []
pednsygraph = R.TGraph(NRUNS+1)
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
    region = int(r)
    rootfile = R.TFile()

    i = 0
    t0 = 0
    for trial in range(runmin, runmax):
	if trial in exclude_runs:
		continue
	print fc[trial]
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
        MPVs.append([fc[i].Get("R"+str(region)+"0_MPV")[0],fc[i].Get("R"+str(region)+"1_MPV")[0],fc[i].Get("R"+str(region)+"2_MPV")[0]])
        #MPVgraph.SetPoint(i,tm[0],MPVs[i])
	print i, MPVs
        MPVgraph0.SetPoint(i,tm[0],MPVs[i][0])
        MPVgraph1.SetPoint(i,tm[0],MPVs[i][1])
        MPVgraph2.SetPoint(i,tm[0],MPVs[i][2])
        MPVgraph0.SetPointError(i,0,.1)
        MPVgraph1.SetPointError(i,0,.1)
        MPVgraph2.SetPointError(i,0,.1)
	for k in xrange(3): 
		mp[k] = MPVs[i][k]
        	mpe[k]=0.1
        #mp[0]=fc[trial].Get("R"+str(region)+"_MPV")[0]
	chi2[0] = fc[trial].Get("Chi20")[0]
	chi2[1] = fc[trial].Get("Chi21")[0]
	chi2[2] = fc[trial].Get("Chi22")[0]
	softgraph.SetPoint(i,tm[0],fc[trial].Get("SoftEvents")[0])
	noisygraph.SetPoint(i,tm[0],fc[trial].Get("NoisyEvents")[0])
#	pednsygraph.SetPoint(i,tm[0],fc[i].Get("PedNoisyEvts")[0])
        #print "Done writing values for trial "+str(trial)

	median_c.append([0,0,0,0])
	median.append([0,0,0,0])
	meanerror = [0,0,0,0]

        for j in xrange(4):
		if j < 3: hist_name = 'R'+str(region)+' Signal_1000Bins_clust' + str(j)
		else: hist_name = 'R'+str(region)+' Signal_1000Bins_clust' 
                #print hist_name, fc[i]
                h = fc[i].Get(hist_name)
		print "1", hist_name
                hentries = h.GetEntries()
                counter = 0
                ticker = 0
                #median_c.append(0)
                meanerror[j] = h.GetMeanError()
                #print trial, median
                while median_c[i][j] == 0:
                        counter += h[ticker]
                        if counter >= hentries/2:
                                median_c[i][j] = ((ticker + 0.5)/10)
                        ticker += 1
                print "The T" + str(trial) + " cluster median is " + str(median_c[i][j])
		if j==0:
                	medgraph_c0.SetPoint(i,tm[0],median_c[i][j])
                	medgraph_c0.SetPointError(i,0,1.2*meanerror[j])
		if j==1:
                	medgraph_c1.SetPoint(i,tm[0],median_c[i][j])
                	medgraph_c1.SetPointError(i,0,1.2*meanerror[j])
		if j==2:
                	medgraph_c2.SetPoint(i,tm[0],median_c[i][j])
                	medgraph_c2.SetPointError(i,0,1.2*meanerror[j])
		if j==3:
                	medgraph_c.SetPoint(i,tm[0],median_c[i][j])
                	medgraph_c.SetPointError(i,0,1.2*meanerror[j])
                #medgraph_cNrm.SetPoint(i,tm[0],median_c[i]/median_c[0])
                #medgraph_cNrm.SetPointError(i,0,1.2*meanerror/median_c[0])
		for k in xrange(3):
                	md_c[k]=median_c[i][k]
                	mde_c[k]=meanerror[k]

                #Getting seed Median values from ROOT file
                if j < 3: hist_name = 'R'+str(region)+' Signal_1000Bins' + str(j)
		else: hist_name = 'R'+str(region)+' Signal_1000Bins'
                #print hist_name, fc[i]
                h = fc[i].Get(hist_name)
		print "2", hist_name
                hentries = h.GetEntries()
                counter = 0
                ticker = 0
                meanerror[j] = h.GetMeanError()
                #print trial, median
                while median[i][j] == 0:
                        counter += h[ticker]
                        if counter >= hentries/2:
                                median[i][j] = ((ticker + 0.5)/10)
                        ticker += 1
                print "The T" + str(trial) + " median is " + str(median[i][j])
                #if (median[i] > himed) and (median[i] < 50) and (tm[0] < 1): himed = median[i]
                #if (median[i] < lomed) and (tm[0] < 4): lomed = median[i]
		if j==0:
                	medgraph0.SetPoint(i,tm[0],median[i][j])
                	medgraph0.SetPointError(i,0,1.2*meanerror[j])
		if j==1:
                	medgraph1.SetPoint(i,tm[0],median[i][j])
                	medgraph1.SetPointError(i,0,1.2*meanerror[j])
		if j==2:
                	medgraph2.SetPoint(i,tm[0],median[i][j])
                	medgraph2.SetPointError(i,0,1.2*meanerror[j])
		if j==3:
                	medgraph.SetPoint(i,tm[0],median[i][j])
                	medgraph.SetPointError(i,0,1.2*meanerror[j])
                #medgraph.SetPoint(i,tm[0],median[i])
                #medgraph.SetPointError(i,0,1.2*meanerror)
                #medgraphNrm.SetPoint(i,tm[0],median[i]/median[0])
                #medgraphNrm.SetPointError(i,0,1.2*meanerror/median[0])
		for k in xrange(3):
                	md_s[k]=median[i][k]
                	mde_s[k]=meanerror[k]


        #print "tree", tm, mp, mpe, md, mde
        RTree.Fill()

	#c2.Print(outfolder+prefix+".ps[")

	hEta = fc[trial].Get("Eta")
	hEta0 = fc[trial].Get("Eta0")
	hEta1 = fc[trial].Get("Eta1")
	hEta2 = fc[trial].Get("Eta2")
	etapct[0] = hEta0.Integral(30,89)/hEta0.Integral()
	etapct[1] = hEta1.Integral(30,89)/hEta1.Integral()
	etapct[2] = hEta2.Integral(30,89)/hEta2.Integral()
	etaary.append(etapct[0])
	etagraph0.SetPoint(i,tm[0],etapct[0])
	etagraph1.SetPoint(i,tm[0],etapct[1])
	etagraph2.SetPoint(i,tm[0],etapct[2])
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

	"""
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
	"""

	sumfile = open ("runsummary.txt", "a")
	sumfile.write (str(abstime)+"\t"+str(starttemp)+"\t"+str(mp[0])+"\t"+str(mp[1])+"\t"+str(mp[2])+"\t"+str(md_s[0])+"\t"+str(md_s[1])+"\t"+str(md_s[2])+"\t"+str(md_c[0])+"\t"+str(md_c[1])+"\t"+str(md_c[2])+"\t"+str(etapct[0])+"\t"+str(etapct[1])+"\t"+str(etapct[2])+"\t"+str(p1)+"\t"+str(p2)+"\n")        
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
MPVgraph0.SetName(prefix+"_MPV0")
MPVgraph0.SetTitle("MPV vs Time")
MPVgraph0.GetXaxis().SetTitle("Days")
MPVgraph0.GetYaxis().SetTitle("ADC Counts")
MPVgraph0.Write("",R.TObject.kOverwrite)
MPVgraph1.SetName(prefix+"_MPV1")
MPVgraph1.SetTitle("MPV vs Time")
MPVgraph1.GetXaxis().SetTitle("Days")
MPVgraph1.GetYaxis().SetTitle("ADC Counts")
MPVgraph1.Write("",R.TObject.kOverwrite)
MPVgraph2.SetName(prefix+"_MPV2")
MPVgraph2.SetTitle("MPV vs Time")
MPVgraph2.GetXaxis().SetTitle("Days")
MPVgraph2.GetYaxis().SetTitle("ADC Counts")
MPVgraph2.Write("",R.TObject.kOverwrite)
medgraph_c.SetName(prefix+"_Median_cluster")
medgraph_c.SetTitle("Cluster Median vs Time")
medgraph_c.GetXaxis().SetTitle("Days")
medgraph_c.GetYaxis().SetTitle("ADC Counts")
medgraph_c.Write("",R.TObject.kOverwrite)
medgraph_c0.SetName(prefix+"_Median_cluster0")
medgraph_c0.SetTitle("Cluster Median vs Time")
medgraph_c0.GetXaxis().SetTitle("Days")
medgraph_c0.GetYaxis().SetTitle("ADC Counts")
medgraph_c0.Write("",R.TObject.kOverwrite)
medgraph_c1.SetName(prefix+"_Median_cluster1")
medgraph_c1.SetTitle("Cluster Median vs Time")
medgraph_c1.GetXaxis().SetTitle("Days")
medgraph_c1.GetYaxis().SetTitle("ADC Counts")
medgraph_c1.Write("",R.TObject.kOverwrite)
medgraph_c2.SetName(prefix+"_Median_cluster2")
medgraph_c2.SetTitle("Cluster Median vs Time")
medgraph_c2.GetXaxis().SetTitle("Days")
medgraph_c2.GetYaxis().SetTitle("ADC Counts")
medgraph_c2.Write("",R.TObject.kOverwrite)
medgraph.SetName(prefix+"_Median")
medgraph.SetTitle("Seed Median vs Time0")
medgraph.GetXaxis().SetTitle("Days")
medgraph.GetYaxis().SetTitle("ADC Counts")
medgraph.Write("",R.TObject.kOverwrite)
medgraph0.SetName(prefix+"_Median0")
medgraph0.SetTitle("Seed Median vs Time0")
medgraph0.GetXaxis().SetTitle("Days")
medgraph0.GetYaxis().SetTitle("ADC Counts")
medgraph0.Write("",R.TObject.kOverwrite)
medgraph1.SetName(prefix+"_Median1")
medgraph1.SetTitle("Seed Median vs Time1")
medgraph1.GetXaxis().SetTitle("Days")
medgraph1.GetYaxis().SetTitle("ADC Counts")
medgraph1.Write("",R.TObject.kOverwrite)
medgraph2.SetName(prefix+"_Median2")
medgraph2.SetTitle("Seed Median vs Time2")
medgraph2.GetXaxis().SetTitle("Days")
medgraph2.GetYaxis().SetTitle("ADC Counts")
medgraph2.Write("",R.TObject.kOverwrite)
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
etagraph0.SetMarkerStyle(3)
etagraph0.SetName(prefix+"_Eta%0")
etagraph0.SetTitle("Eta % .2-.8 vs Time")
etagraph0.GetXaxis().SetTitle("Days")
etagraph0.GetYaxis().SetTitle("Percent")
etagraph0.Write("",R.TObject.kOverwrite)
etagraph1.SetMarkerStyle(3)
etagraph1.SetName(prefix+"_Eta%1")
etagraph1.SetTitle("Eta % .2-.8 vs Time")
etagraph1.GetXaxis().SetTitle("Days")
etagraph1.GetYaxis().SetTitle("Percent")
etagraph1.Write("",R.TObject.kOverwrite)
etagraph2.SetMarkerStyle(3)
etagraph2.SetName(prefix+"_Eta%2")
etagraph2.SetTitle("Eta % .2-.8 vs Time")
etagraph2.GetXaxis().SetTitle("Days")
etagraph2.GetYaxis().SetTitle("Percent")
etagraph2.Write("",R.TObject.kOverwrite)
dmedgraph.Write("Seed_Med_Der",R.TObject.kOverwrite)
dmedcgraph.Write("Clust_Med_Der",R.TObject.kOverwrite)
detagraph.Write("Eta_Der",R.TObject.kOverwrite)

c1.cd(1)
MPVgraph1.SetLineColor(2)
MPVgraph2.SetLineColor(3)
MPVgraph0.Draw()
MPVgraph1.Draw("same")
MPVgraph2.Draw("same")
c1.cd(2)
medgraph_c1.SetLineColor(2)
medgraph_c2.SetLineColor(3)
medgraph_c0.Draw()
medgraph_c1.Draw("same")
medgraph_c2.Draw("same")
c1.cd(3)
medgraph1.SetLineColor(2)
medgraph2.SetLineColor(3)
medgraph0.Draw()
medgraph1.Draw("same")
medgraph2.Draw("same")
c1.cd(4)
etagraph1.SetLineColor(2)
etagraph2.SetLineColor(3)
etagraph0.Draw()
etagraph1.Draw("same")
etagraph2.Draw("same")
c1.Update()
c1.Print(outfolder+prefix+".pdf")

RFile.Close()

