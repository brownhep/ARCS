import ROOT as R
import sys
import os.path
from array import array

#infolder = "./rootfiles/" #where the root files are. a folder that contains nonclus/----.root and clus/----.root
#outfolder = "./" #where to place the output
#runmin = 0 #minimum run to check.
#runmin = sys.argv[1]
#runmax = sys.argv[2] #maximum run to check
runinfo = sys.argv[1]

def getsimval(value,simdata):
	simval = float(simdata[1][0])
	i = 1
	while ((i < (len(simdata)-1)) and (float(simdata[i][3]) > value)):
		i += 1
	if i > 1: simval = float(simdata[i-1][0]) + (float(simdata[i][0])-float(simdata[i-1][0]))*(value - float(simdata[i-1][3]))/(float(simdata[i][3]) - float(simdata[i-1][3]))
	#print "simval", i, simval, value, simdata[i][3], simdata[i-1][3], simdata[i-1][0]
	return(simval)

def getmedian(hist):
        hentries = hist.GetEntries()
        counter = 0
        ticker = 0
        median = 0
        meanerror = h.GetMeanError()
        while median == 0:
            counter += hist[ticker]
            if counter >= hentries/2:
                median = ((ticker + 0.5)/10)
            ticker += 1
        print "The median is " + str(median)
	return(median)

#Get Run information from currentruninfo.txt
f = open(runinfo,"r")
prefix = f.readline()[:-1]
rawdata = f.readline()[:-1]
infolder = f.readline()[:-1]
regline = f.readline()[:-1]
regions = regline.split(' ')
biasv = f.readline()[:-1]
runmin = f.readline()[:-1]
runmax = f.readline()[:-1]
outfolder = infolder
#print prefix, folder, regions
f.close()

runmin = int(runmin)
runmax = int(runmax)

hhits = R.TH1I("hhits","Hit Distribution by Strip",32,0,32)
MPVs = []
MPVgraph = R.TGraphErrors(runmax-runmin+1)
median = []
median_c = []
medgraph = R.TGraphErrors(runmax-runmin+1)
medgraph_c = R.TGraphErrors(runmax-runmin+1)
medgraphNrm = R.TGraphErrors(runmax-runmin+1)
medgraph_cNrm = R.TGraphErrors(runmax-runmin+1)
MPVgraphNrm = R.TGraphErrors(runmax-runmin+1)
etagraph = R.TGraphErrors(runmax-runmin+1)
simgraph = R.TGraph(runmax-runmin+1)
softevts = []
softgraph = R.TGraph(runmax-runmin+1)
noisyevts = []
noisygraph = R.TGraph(runmax-runmin+1)
pednsyevts = []
pednsygraph = R.TGraph(runmax-runmin+1)
dmedgraph = R.TGraph(runmax - runmin - 3)
dmedcgraph = R.TGraph(runmax - runmin - 3)
detagraph = R.TGraph(runmax - runmin - 3)

#if os.path.isfile(outfolder+"_"+prefix+"_Summary.root"): RFile = R.TFile(outfolder+"_"+prefix+"_Summary.root",'UPDATE')
#else: RFile = R.TFile(outfolder+"_"+prefix+"_Summary.root",'RECREATE')

timeary = []
etaary = []
chimax = 1
chimaxeta = 1
pmedmax = 0
pmedcmax = 0
petamax = 0
himed = 0
lomed = 100


hdfile = R.TFile(infolder+prefix+"_hd.root","UPDATE")
#hseed0 = R.TH2F()
#hprof0 = R.TProfile()

hits = hdfile.Get("hits")
"""
hits.Draw("hit_strip>>hhitsB")
hhits = R.gPad.GetPrimitive("hhitsB")
hhits.Fit("gaus")
f1 = hhits.GetFunction("gaus")
p0 = f1.GetParameter(0)
p1 = f1.GetParameter(1)
p2 = f1.GetParameter(2)
hits_chi2 = f1.GetChisquare()
"""

#lostrip = int(p1 - p2)
#histrip = int(p1+p2)
lostrip = 7
histrip = 8
print lostrip, histrip
#cut1 = R.TCut('"hit_strip>=' + str(lostrip) + ' && hit_strip<=' + str(histrip) + '"')
#cut2 = R.TCut('"hit_strip<' + str(lostrip) + ' || hit_strip>' + str(histrip) + '"')
#hits.Draw("strip_charge:runno>>hseed0B")
#hits.Draw("strip_charge:runno>>hseed0B","","colz")
#R.gPad.GetPrimitive("hseed0B").ProfileX().Write("SeedMid",R.TObject.kOverwrite)
#hseed0 = R.gPad.GetPrimitive("hseed0B").Clone()
#hprof0 = hseed0.ProfileX()
#hprof0 = hits.Draw("strip_charge:runno").ProfileX()
#hprof0.Draw()

print lostrip, histrip
#hits.Draw('strip_charge:runno>>hseed1B', cut2)
hits.Draw("""runno>>hseed1B""")
#hits.Draw('strip_charge:runno>>hseed1B',cut1)
#hits.Draw("strip_charge:runno>>hseed1B","","colz")
R.gPad.GetPrimitive("hseed1B").Write("SeedOuter",R.TObject.kOverwrite)
#hseed1 = R.gPad.GetPrimitive("hseed1B").Clone()
#hprof1 = hseed1.ProfileX()


#hprof0.Write("proftest",R.TObject.kOverwrite)
#hseed0.Write("htest",R.TObject.kOverwrite)
hdfile.Close()

"""
c2.Write("",R.TObject.kOverwrite)
RTree.Write("",R.TObject.kOverwrite)
MPVgraph.SetName(prefix+"_MPV")
MPVgraph.SetTitle("MPV vs Time")
MPVgraph.GetXaxis().SetTitle("Days")
MPVgraph.GetYaxis().SetTitle("ADC Counts")
MPVgraph.Write("",R.TObject.kOverwrite)
MPVgraphNrm.SetName(prefix+"_MPV_Nrm")
MPVgraphNrm.SetTitle("MPV vs Time")
MPVgraphNrm.GetXaxis().SetTitle("Days")
MPVgraphNrm.GetYaxis().SetTitle("Normalized Charge")
MPVgraphNrm.Write("",R.TObject.kOverwrite)
simgraph.Write("Sim Graph",R.TObject.kOverwrite)

c1.cd(1)
MPVgraph.Draw()
c1.Update()
#c1.SaveAs(outfolder+prefix+"_MPV.jpg")
medgraph_c.SetName(prefix+"_Median_cluster")
medgraph_c.SetTitle("Cluster Median vs Time")
medgraph_c.GetXaxis().SetTitle("Days")
medgraph_c.GetYaxis().SetTitle("ADC Counts")
medgraph_c.Write("",R.TObject.kOverwrite)
medgraph_cNrm.SetName(prefix+"_Median_cluster_Nrm")
medgraph_cNrm.SetTitle("Cluster Median vs Time")
medgraph_cNrm.GetXaxis().SetTitle("Days")
medgraph_cNrm.GetYaxis().SetTitle("Normalized Charge")
medgraph_cNrm.Write("",R.TObject.kOverwrite)
c1.cd(2)
medgraph_c.Draw()
c1.Update()
#c1.SaveAs(outfolder+prefix+"_med_clust.jpg")
medgraph.SetName(prefix+"_Median")
medgraph.SetTitle("Seed Median vs Time")
medgraph.GetXaxis().SetTitle("Days")
medgraph.GetYaxis().SetTitle("ADC Counts")
medgraph.Write("",R.TObject.kOverwrite)
medgraphNrm.SetName(prefix+"_Median_Nrm")
medgraphNrm.SetTitle("Seed Median vs Time")
medgraphNrm.GetXaxis().SetTitle("Days")
medgraphNrm.GetYaxis().SetTitle("Normalized Charge")
medgraphNrm.Write("",R.TObject.kOverwrite)
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
dmedgraph.Write("Seed_Med_Der",R.TObject.kOverwrite)
dmedcgraph.Write("Clust_Med_Der",R.TObject.kOverwrite)
detagraph.Write("Eta_Der",R.TObject.kOverwrite)
RFile.Close()

"""
