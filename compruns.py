import ROOT as R
import time

#filefolder = ["/FTH200Y_LTR4_7/", "/FTH200Y_closesr90_R6/", "/FTH200Y_closesr90_R7/", "/FTH200Y_closesr90_R8/", "/FTH200Y_closesr90_R9/","/FTH200Y_closesr90_R1/","/FTH200Y_closesr90_R2/"]
#prefix = ["FTH200Y_LTR4_7", "FTH200Y_closesr90_R6", "FTH200Y_closesr90_R7_b", "FTH200Y_7_closesr90_LTR_R8", "FTH200Y_closesr90_R9", "FTH200Y_closesr90_R1", "FTH200Y_closesr90_R2"]
#desc = ["R4 Far Sr90", "R6 Close Sr90", "R7 Close Sr90", "R8 Close Sr90", "R9 Close Sr90", "R1 Close Sr90", "R2 Close Sr90"]
#region = [4,6,7,8,9,1,2]
#pitch = [120, 80, 240, 120, 70, 70, 80]

#Only near source runs
filefolder = ["/FTH200Y_closesr90_R7/", "/FTH200Y_closesr90_R8/", "/FTH200Y_closesr90_R6/", "/FTH200Y_closesr90_R9/","/FTH200Y_closesr90_R2/","/FTH200Y_closesr90_R1/"]
prefix = ["FTH200Y_closesr90_R7_b", "FTH200Y_7_closesr90_LTR_R8", "FTH200Y_closesr90_R6", "FTH200Y_closesr90_R9", "FTH200Y_closesr90_R2", "FTH200Y_closesr90_R1"]
desc = ["R7 Close Sr90", "R8 Close Sr90", "R6 Close Sr90", "R9 Close Sr90", "R2 Close Sr90", "R1 Close Sr90"]
region = [6,5,7,4,11,12]
pitch = [240, 120, 80, 70, 80, 70]
implant = [58, 28, 18, 8.5, 26, 22.5]
runstart = [0, -1, 0, 4, 0, 0]
runend = [197, 181, 294, 176, 750, 430]

hitchart = R.TH1I("hit_strips","Hit Strips", 32, 0, 32)
nruns = len(region)
dqdt0 = R.TGraph(nruns)
dqdt05 = R.TGraph(nruns)
dqdt1 = R.TGraph(nruns)
dqdt15 = R.TGraph(nruns)
dqdt2 = R.TGraph(nruns)
dqdt25 = R.TGraph(nruns)
dqdt3 = R.TGraph(nruns)
dqdt35 = R.TGraph(nruns)
dqdt4 = R.TGraph(nruns)
dqdt = R.TMultiGraph()
mpvgraph = R.TMultiGraph()
medgraph = R.TMultiGraph()
medcgraph = R.TMultiGraph()
mpvgraphNrm = R.TMultiGraph()
medgraphNrm = R.TMultiGraph()
medcgraphNrm = R.TMultiGraph()
simgraph = R.TMultiGraph()
softgraph = R.TMultiGraph()
nsygraph = R.TMultiGraph()
etagraph = R.TMultiGraph()
pnsgraph = R.TMultiGraph()
nsgraph = R.TMultiGraph()

mpvgraph.SetTitle("MPV Langaus Fit vs Time;Time (Days);MPV (ADC Counts)")
medgraph.SetTitle("Strip Charge Median vs Time;Time (Days);Strip Median (ADC Counts)")
medcgraph.SetTitle("Cluster Charge Median vs Time;Time (Days);Cluster Median (ADC Counts)")
mpvgraphNrm.SetTitle("MPV Langaus Fit vs Time;Time (Days);MPV (ADC Counts)")
medgraphNrm.SetTitle("Strip Charge Median vs Time;Time (Days);Strip Median (ADC Counts)")
medcgraphNrm.SetTitle("Cluster Charge Median vs Time;Time (Days);Cluster Median (ADC Counts)")
softgraph.SetTitle("Soft Events vs Time;Time (Days);# Soft Events")
nsygraph.SetTitle("Noisy Events vs Time;Time (Days);# Noisy Events")
etagraph.SetTitle("Fraction Events Eta between 0.2-0.8 vs Time;Time (Days);Fraction")
pnsgraph.SetTitle("Prepedestal Noise vs Time;Time (Days);Noise")
nsgraph.SetTitle("Pedestal Noise vs Time;Time (Days);Noise")


#Creates Root File to store Plots 
RFile_name = 'RunCompare.root'
RFile = R.TFile(RFile_name, 'RECREATE')
RFile.Close()

c1 = R.TCanvas( 'Noise', 'Noise', 200, 10, 800, 1000 )
c1.SetTitle("Noise")
c1.Divide(1,2)
#c6 = R.TCanvas( 'First/Last', 'Noise', 200, 10, 800, 1000 )
#c6.SetTitle("FirstLast")
#c6.Divide(1,2)

hnoisestack = R.THStack("noise","Noise vs Time")
hhitsstack = R.THStack("HitD","Hit Distribution")
hnoisestack.Paint("nostack")
hhitsstack.Paint("nostack")
#profnoise = []
#hnoise = []
hhits = []
fc = []

for i in xrange(len(filefolder)):
	RFileName = "rootfiles" + filefolder[i]+ "_" + prefix[i]+"_Summary.root"	
	fc.append(R.TFile(RFileName))
	print RFileName


for i in xrange(len(filefolder)):
	RFirstName = "rootfiles" + filefolder[i] + prefix[i]+"_" + str(runstart[i]) + ".root"
	RLastName = "rootfiles" + filefolder[i] + prefix[i]+"_" + str(runend[i]) + ".root"
	fc.append(R.TFile(RFirstName))
	fc.append(R.TFile(RLastName))
	print RFirstName, RLastName
	#RFirst = R.TFile(RFirstName, "read")
	#RLast = R.TFile(RLastName, "read")
	#RFirst.Close()
	#RLast.Close()

	
RFile = R.TFile(RFile_name,"UPDATE")

legend = R.TLegend(0.6,0.15,0.89,0.4)
urlegend = R.TLegend(0.6,0.6,0.89,0.85)
dqdtlegend = R.TLegend(0.6,0.6,0.89,0.85)

for i in xrange(len(filefolder)):

	print "Opening rootfiles" + filefolder[i] + "_" + prefix[i] + "_Summary.root"
	henv2 = R.TH1F()	
	henv2.SetOption("L*")
	hmpv = fc[i].Get(prefix[i]+"_MPV")
	hmed = fc[i].Get(prefix[i]+"_Median")
	hmedc = fc[i].Get(prefix[i]+"_Median_cluster")
	hmpvN = fc[i].Get(prefix[i]+"_MPV_Nrm")
	hmedN = fc[i].Get(prefix[i]+"_Median_Nrm")
	hmedcN = fc[i].Get(prefix[i]+"_Median_cluster_Nrm")
	hsoft = fc[i].Get(prefix[i]+"_softevts")
	hnsy = fc[i].Get(prefix[i]+"_nsyevts")
	heta = fc[i].Get(prefix[i]+"_Eta%")
	hltr = fc[i].Get("ltr")
	hsim = fc[i].Get("Sim Graph")
	oldxp = 0
	for j in xrange(hmed.GetN()):
		xp = R.Double(0.0)
		ys = R.Double(0.0)
		yc = R.Double(0.0)
		ye = R.Double(0.0)
		hmed.GetPoint(j,xp,ys)
		hmedc.GetPoint(j,xp,yc)
		heta.GetPoint(j,xp,ye)
		#print i, xp, pitch[i], implant[i], yc, ys
		invoxw = 1/(float(pitch[i])-implant[i])
		if xp == 0: 
			dqdt0.SetPoint(i,invoxw,yc-ys)
			print i,invoxw,yc-ys
		if (xp>0.5) and (oldxp<0.5): dqdt05.SetPoint(i,invoxw,yc-ys)
		if (xp>1) and (oldxp<1): dqdt1.SetPoint(i,invoxw,yc-ys)
		if (xp>1.5) and (oldxp<1.5): dqdt15.SetPoint(i,invoxw,yc-ys)
		if (xp>2) and (oldxp<2): dqdt2.SetPoint(i,invoxw,yc-ys)
		if (xp>2.5) and (oldxp<2.5): dqdt25.SetPoint(i,invoxw,yc-ys)
		if (xp>3) and (oldxp<3): dqdt3.SetPoint(i,invoxw,yc-ys)
		if (xp>3.5) and (oldxp<3.5): dqdt35.SetPoint(i,invoxw,yc-ys)
		if (xp>4) and (oldxp<4): dqdt4.SetPoint(i,invoxw,yc-ys)
		oldxp = xp
		#print "hey",hmed.GetN(),xp,ys,yc,ye
	henv = R.TH1F()	
	hltr.Draw("temp:time>>henv"+str(i),"","L*")
	rundesc = "R" + str(13 - region[i])
	#R.gPad.GetPrimitive("henv"+str(i)).Clone().Write("Env_" + rundesc)
	henv2 = R.gPad.GetPrimitive("henv"+str(i)).Clone()
	henv2.Write("Env_" + rundesc)
	legend.AddEntry(hmpv, "R" + str(region[i]) + ", " + str(pitch[i]) + " um", "l")
	urlegend.AddEntry(hmpv, "R" + str(region[i]) + ", " + str(pitch[i]) + " um", "l")
	hmpv.Write("MPV_" + rundesc)
	hmed.Write("SeedMed_" + rundesc)
	hmedc.Write("ClustMed_" + rundesc)
	hsoft.Write("SoftEvents_" + rundesc)
	hnsy.Write("NoisyEvents_" + rundesc)
	heta.Write("Eta%_" + rundesc)
	#henv2.Write("Env_" + str(i))

	gwidth = fc[i].Get("gaus_p2")[0]
	spotsize = 4*gwidth*pitch[i]
	print i, spotsize

	#heta2 = fc[i].Get("Eta")
	#heta2.Write("Eta_" + str(i))

	print len(filefolder)+2*i, "R"+str(13-region[i])+" Signal_100Bins_clust"
	print fc[len(filefolder)+2*i]
	hqdist = fc[len(filefolder)+2*i].Get("R"+str(region[i])+" Signal_100Bins_clust")
	hqdist2 = fc[len(filefolder)+2*i+1].Get("R"+str(region[i])+" Signal_100Bins_clust")
	hqsdist = fc[len(filefolder)+2*i].Get("R"+str(region[i])+" Signal_1000Bins")
	hqsdist2 = fc[len(filefolder)+2*i+1].Get("R"+str(region[i])+" Signal_1000Bins")
	hetadist = fc[len(filefolder)+2*i].Get("Eta")
	hetadist2 = fc[len(filefolder)+2*i+1].Get("Eta")
	hqdist2.SetLineColor(2)
	hqsdist2.SetLineColor(2)
	hetadist2.SetLineColor(2)
	hqdist.Write("Qdist0_R"+str(13-region[i]),R.TObject.kOverwrite)
	hqdist2.Write("QdistF_R"+str(13-region[i]),R.TObject.kOverwrite)
	hqsdist.Write("QSdist0_R"+str(13-region[i]),R.TObject.kOverwrite)
	hqsdist2.Write("QSdistF_R"+str(13-region[i]),R.TObject.kOverwrite)
	hetadist.Write("Etadist0_R"+str(13-region[i]),R.TObject.kOverwrite)
	hetadist2.Write("EtadistF_R"+str(13-region[i]),R.TObject.kOverwrite)
	#c6.cd(1)
	#hqdist.Draw()
	#hqdist.Draw("same")	
	#c6.cd(2)
	#hetadist.Draw()
	#hetadist.Draw("same")	
	#c6.Update()
	#c6.Write("FirstLast_R"+str(13-region[i]),R.TObject.kOverwrite)

	c1.cd(1)
        print "Drawing noise"
	profnoise = fc[i].Get("hpns_tm")
	hnoise = (profnoise.DrawCopy())
        hnoise.SetLineColor(i + 1)
	hnoise.SetOption("L")
	hnoise.GetYaxis().SetRangeUser(0,4)
	hnoise.Write("Noise_R" + str(13-region[i]))
	hnoisestack.Add(hnoise)
        if i==0: profnoise.Draw()
        else: profnoise.Draw("same")
        #if i==0: hnoise.Draw()
        #else: hnoise.Draw("same")
        c1.Update()

	c1.cd(2)
        hhits = fc[i].Get("hhits2")
        hhits.SetLineColor(i + 1)
        #hhits.SetOption("0")
        #hhits.SetOption("L")
	hhits.GetFunction("gaus").Delete()
        normC = hhits.Integral()
        print "Integral value: ", normC
        hhits.Scale(1/normC)
	hhits.Write("Hits_R" + str(13-region[i]))
        if i==0: hhits.Draw()
        else: hhits.Draw("same")
	hhitsstack.Add(hhits)
        c1.Update()

	hmpv.SetLineColor(i+1)
	hmed.SetLineColor(i+1)
	hmedc.SetLineColor(i+1)
	hmpvN.SetLineColor(i+1)
	hmedN.SetLineColor(i+1)
	hmedcN.SetLineColor(i+1)
	hsoft.SetLineColor(i+1)
	hnsy.SetLineColor(i+1)
	heta.SetLineColor(i+1)
	hsim.SetLineColor(i+1)
	#hpns.SetLineColor(i+1)
	#hns.SetLineColor(i+1)
	hmpv.SetMarkerColor(i+1)
	hmed.SetMarkerColor(i+1)
	hmedc.SetMarkerColor(i+1)
	hsoft.SetMarkerColor(i+1)
	hnsy.SetMarkerColor(i+1)
	heta.SetMarkerColor(i+1)
	#hpns.SetMarkerColor(i+1)
	#hns.SetMarkerColor(i+1)
	#hmpv.SetMarkerStyle(3)
	#hmed.SetMarkerStyle(3)
	#hmedc.SetMarkerStyle(3)
	hsoft.SetMarkerStyle(3)
	hnsy.SetMarkerStyle(3)
	heta.SetMarkerStyle(3)
	#hpns.SetMarkerStyle(3)
	#hns.SetMarkerStyle(3)

	mpvgraph.Add(hmpv)
	medgraph.Add(hmed)
	medcgraph.Add(hmedc)
	mpvgraphNrm.Add(hmpvN)
	medgraphNrm.Add(hmedN)
	medcgraphNrm.Add(hmedcN)
	simgraph.Add(hsim)
	softgraph.Add(hsoft)
	nsygraph.Add(hnsy)
	etagraph.Add(heta)
	#pnsgraph.Add(hpns)
	#nsgraph.Add(hns)


	#mpvgraph.Add(fc[i].Get(prefix[i]+"_MPV"))
	#medgraph.Add(fc[i].Get(prefix[i]+"_Median"))
	#medcgraph.Add(fc[i].Get(prefix[i]+"_Median_cluster"))
	#softgraph.Add(fc[i].Get(prefix[i]+"_softevts"))
	#nsygraph.Add(fc[i].Get(prefix[i]+"_nsyevts"))
	#etagraph.Add(fc[i].Get(prefix[i]+"_Eta%"))


dqdt0.SetMarkerColor(1)
dqdt05.SetMarkerColor(2)
dqdt1.SetMarkerColor(3)
dqdt15.SetMarkerColor(4)
dqdt2.SetMarkerColor(5)
dqdt25.SetMarkerColor(6)
dqdt3.SetMarkerColor(7)
dqdt35.SetMarkerColor(8)
dqdt4.SetMarkerColor(9)
dqdt0.SetMarkerStyle(7)
dqdt05.SetMarkerStyle(7)
dqdt1.SetMarkerStyle(7)
dqdt15.SetMarkerStyle(7)
dqdt2.SetMarkerStyle(7)
dqdt25.SetMarkerStyle(7)
dqdt3.SetMarkerStyle(7)
dqdt35.SetMarkerStyle(7)
dqdt4.SetMarkerStyle(7)
dqdt.Add(dqdt0)
dqdt.Add(dqdt05)
dqdt.Add(dqdt1)
dqdt.Add(dqdt15)
dqdt.Add(dqdt2)
dqdt.Add(dqdt25)
dqdt.Add(dqdt3)
dqdt.Add(dqdt35)
dqdt.Add(dqdt4)
dqdtlegend.AddEntry(dqdt0, "t=0","l")
dqdtlegend.AddEntry(dqdt05, "t=0.5","l")
dqdtlegend.AddEntry(dqdt1, "t=1","l")
dqdtlegend.AddEntry(dqdt15, "t=1.5","l")
dqdtlegend.AddEntry(dqdt2, "t=2","1")
dqdtlegend.AddEntry(dqdt25, "t=2.5","l")
dqdtlegend.AddEntry(dqdt3, "t=3","1")
dqdtlegend.AddEntry(dqdt35, "t=3.5","l")
dqdtlegend.AddEntry(dqdt4, "t=4","l")

#RFile = R.TFile(RFile_name,"UPDATE")

c2 = R.TCanvas( 'Summary', 'Charge Collection vs Time', 200, 10, 800, 800 )
c2.Divide(2,2)

c2.cd(1)
mpvgraph.Draw("a")
legend.Draw()
c2.cd(2)
medgraph.Draw("a")
legend.Draw()
c2.cd(3)
medcgraph.Draw("a")
legend.Draw()
c2.cd(4)
etagraph.Draw("a")
legend.Draw()
c2.Update()
c2.Write("",R.TObject.kOverwrite)

c3 = R.TCanvas( 'Summary2', 'Run Data', 200, 10, 800, 800 )
c3.Divide(2,2)
R.gStyle.SetOptStat(0)

c3.cd(1)
#N0 = RFile.Get("Noise_0")
#N1 = RFile.Get("Noise_1")
#N2 = RFile.Get("Noise_2")
#N3 = RFile.Get("Noise_3")
#N4 = RFile.Get("Noise_4")
#N0.Draw()
#N1.Draw("same")
#N2.Draw("same")
#N3.Draw("same")
#N4.Draw("same")
legend.Draw()
c3.cd(2)
hhitsstack.Draw("0nostack")
legend.Draw()
c3.Update
c3.Write("RunData")

c4 = R.TCanvas( 'SeedMed', 'Run Data', 200, 10, 800, 800 )

c4.cd(1)
medgraph.Draw("a")
legend.Draw()
c4.Update()
c4.Write("Seed Median")

c5 = R.TCanvas( 'ClustMed', 'Run Data', 200, 10, 800, 800 )
c5.cd(1)
medcgraph.Draw("a")
legend.Draw()
c5.Update()
c5.Write("Cluster Median")

print "Writing graphs"
mpvgraph.Write("MPV",R.TObject.kOverwrite)
medgraph.Write("Median",R.TObject.kOverwrite)
medcgraph.Write("Median_cluster",R.TObject.kOverwrite)
mpvgraphNrm.Write("MPV_Nrm",R.TObject.kOverwrite)
medgraphNrm.Write("Median_Nrm",R.TObject.kOverwrite)
medcgraphNrm.Write("Median_cluster_Nrm",R.TObject.kOverwrite)
simgraph.Write("Sim_Graph",R.TObject.kOverwrite)
#softgraph.Draw("*")
softgraph.Write("Soft_Events",R.TObject.kOverwrite)
nsygraph.Write("Noisy_Events",R.TObject.kOverwrite)
etagraph.Write("Eta%",R.TObject.kOverwrite)
#pnsgraph.Write("Preped_Noise",R.TObject.kOverwrite)
#nsgraph.Write("Ped_Noise",R.TObject.kOverwrite)
c1.Write("",R.TObject.kOverwrite)
hnoisestack.Write("",R.TObject.kOverwrite)
hhitsstack.Paint("nostack")
hhitsstack.Draw("nostack")
hhitsstack.Write("",R.TObject.kOverwrite)
dqdt.Write("dqdt",R.TObject.kOverwrite)
legend.Write("lrlegend")
urlegend.Write("urlegend")
dqdtlegend.Write("dqdtlegend")
RFile.Close()

