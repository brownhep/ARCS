import ROOT as R
from Methods_pedcomp import *
import time

filenames = ["Raw_Data_Ped_IntTrg.dat", "Raw_Data_Ped_ExtTrgLat4.dat", "Raw_Data_Ped_ExtTrgLat25.dat"]

runno = array('i',[0])
strip = array('i',[0])
pd = array('f',[0.])
noise = array('f',[0.])

RTree = R.TTree('strips','Strip Info')
RTree.Branch('run',runno,'runno/I')
RTree.Branch('strip',strip,'strip/I')
RTree.Branch('pd',pd,'pd/F')
RTree.Branch('noise',noise,'noise/F')


#Creates Root File to store Plots 
RFile_name = 'PedCompare.root'
RFile = R.TFile(RFile_name, 'RECREATE')
RFile.Close()

i = 0
for file in filenames:
		
	#Generates the Pre-Pedestal
	print "Prepedestal for " + file
	preped = get_preped(file, 'PrePed_' + str(i), RFile_name, 1)

	#Fill Tree of Strip Information
	for x in xrange(512):
		runno[0] = i
		strip[0] = x
		pd[0] = preped.GetBinContent(x+1) 
		noise[0] = preped.GetBinError(x+1)*R.sqrt(preped.GetBinEntries(x+1))
		RTree.Fill()

	i += 1
				
RFile = R.TFile(RFile_name, 'UPDATE')
RTree.Write("",R.TObject.kOverwrite)
RFile.Close()

