import ROOT as R
import sys
import time
import os.path
from datetime import datetime, date, time, timedelta
from array import array

#R.gROOT.ProcessLine('.L /user_data/agarabed/ARCS/src/C++/LandauFit.C+')
R.gROOT.ProcessLine('.L /Code/LandauFit.C+')

def get_tempdata(file_name, outfolder, filePrefix):

    time = array('f',[0.])
    dewp = array('f',[0.])
    Vpelt = array('f',[0.])
    Ipelt = array('f',[0.])
    chuckT = array('f',[0.])
    airT = array('f',[0.])
    RH = array('f',[0.])

    RTree = R.TTree('env','Environment Data')
    RTree.Branch('time',time,'time/F')
    RTree.Branch('dewp',dewp,'dewp/F')
    RTree.Branch('Vpelt',Vpelt,'Vpelt/F')
    RTree.Branch('Ipelt',Ipelt,'Ipelt/F')
    RTree.Branch('chuckT',chuckT,'chuckT/F')
    RTree.Branch('airT',airT,'airT/F')
    RTree.Branch('RH',RH,'RH/F')

    hchuck = R.TGraph()
    hdp = R.TGraph()
    hrh = R.TGraph()
    hair = R.TGraph()

    #Opens environmental data file
    print "Reading in environmental data from file: ", file_name
    if os.path.isfile(file_name):
        env_file = open(file_name,'r')
        cnt = 0
        #temp_data = [[0 for x in xrange(7)]]
	temp_data = []
        t_data = [0 for x in xrange(7)]
	t0 = 0
        for line in env_file:
            env_data = line.split('\t')
            for i in xrange(7): t_data[i] = float(env_data[i])
            temp_data.append([])
            for i in xrange(7): temp_data[cnt].append(t_data[i])		
            if t0 == 0: t0 = float(env_data[0])/(60*60*24)
            time[0] = float(env_data[0])/(60*60*24) - t0
            dewp[0] = float(env_data[1])
            chuckT[0] = float(env_data[2])
            airT[0] = float(env_data[3])
            RH[0] = float(env_data[4])
            Vpelt[0] = float(env_data[5])
            Ipelt[0] = float(env_data[6])
            RTree.Fill()
	    hchuck.SetPoint(cnt, time[0], chuckT[0])
	    hdp.SetPoint(cnt, time[0], dewp[0])
	    hrh.SetPoint(cnt, time[0], RH[0])
	    hair.SetPoint(cnt, time[0], airT[0])
            cnt += 1

	if os.path.isfile(outfolder+filePrefix+"_Summary.root"): RFile = R.TFile(outfolder+filePrefix+"_Summary.root",'UPDATE')
        else:  RFile = R.TFile(outfolder+filePrefix+"_Summary.root",'CREATE')
        RTree.Write("",R.TObject.kOverwrite)
	hchuck.SetName("ChuckT")
	hchuck.SetTitle("Chuck Temp vs Time")
	hchuck.GetXaxis().SetTitle("Time (Days)")
	hchuck.GetYaxis().SetTitle("T Chuck (C)")
	hchuck.Write("",R.TObject.kOverwrite)
	hdp.SetName("DewPt")
	hdp.SetTitle("Dew Point vs Time")
	hdp.GetXaxis().SetTitle("Time (Days)")
	hdp.GetYaxis().SetTitle("Dew Point (C)")
	hdp.Write("",R.TObject.kOverwrite)
	hrh.SetName("RH")
	hrh.SetTitle("Humidity vs Time")
	hrh.GetXaxis().SetTitle("Time (Days)")
	hrh.GetYaxis().SetTitle("Humidity (%)")
	hrh.Write("",R.TObject.kOverwrite)
	hair.SetName("AirT")
	hair.SetTitle("Air Temp vs Time")
	hair.GetXaxis().SetTitle("Time (Days)")
	hair.GetYaxis().SetTitle("T Air (C)")
	hair.Write("",R.TObject.kOverwrite)
        RFile.Close()

    else: 
        print "Environmental data file does not exist"
        temp_data = 0

    #print temp_data
    return temp_data


def get_temp(t_data, time, start=0):

    chuckT = [0,0]

    if t_data != 0:
        ti0 = t_data[0][0]
        Ti0 = t_data[0][2]
    	for i in xrange(start,len(t_data)):
	    #print 'debug ', i, t_data[i][0], time, t_data[i][2]
            if t_data[i][0] < time:
                ti0 = t_data[i][0]
                Ti0 = t_data[i][2]
            	#print 'a',ti0,time,float(ti0)-float(time)
            	continue
            else:
                ti = t_data[i][0]
                Ti = t_data[i][2]
		if ti == ti0: chuckT = [Ti0,0]
                else: chuckT = [Ti0 + (time-ti0)*(Ti-Ti0)/(ti-ti0),i-1]
                break

    return chuckT


def get_preped(file_name, title, region, RFile_name = '', T_Data=0, scale = 1, Pedestal2 = None):

    #Sets whether you want results in ADC or Electrons
    print 'SCALE:',scale
    
    #Opens data file with pedestal information
    if file_name.find("Raw_Data_") == -1: exefile = False
    else: exefile = True
    print "Old file: ", exefile
    ped_file = open(file_name,'r')
    
    #Creates the TProfile which stores the information about channel averages and noise
    Ped_Data = R.TProfile('Ped Data ' + title,'Ped Data ' + title,512,0,512)
    Ped_Data.Sumw2() #Calculates TRUE average
    Ped_Data.SetOption('colz')
    Ped_CM = R.TH1F('PrepedCM','Preped CM',512,0,512)


    APV0_Data = R.TH2I('APV0','APV0',128,0,128,100,0,100)
    APV1_Data = R.TH2I('APV1','APV1',128,0,128,100,0,100)
    APV2_Data = R.TH2I('APV2','APV2',128,0,128,100,0,100)
    APV3_Data = R.TH2I('APV3','APV3',128,0,128,100,0,100)
    APV0_Data.SetOption('colz')
    APV1_Data.SetOption('colz')
    APV2_Data.SetOption('colz')
    APV3_Data.SetOption('colz')
    Noise_Region = R.TProfile('RegNoise','Noise by Region',16,0,16)

    #Creates TObject to store time
    PedStartTime = R.TVectorF(1)
    PedStartTemp = R.TVectorF(1)
    PedNsyEvts = R.TVectorF(1)

    stp = array('i',[0])
    ped = array('f',[0.])
    noise = array('f',[0.])

    RTree = R.TTree('ppd','Ped_Data')
    RTree.Branch('stp',stp,'stp/I')
    RTree.Branch('ped',ped,'ped/F')
    RTree.Branch('noise',noise,'noise/F')

    #Reads in Data and stores in TProfile hi
    event_data = [] #stores data from 512 channels of 1 event
    event = 0 #Counts the number of events
    NoisyEvts = 0 #Counts the number of events
    tmstamp = 0

    for line in ped_file:
        #Read out time from file
        if line[0:4] == 'Date':
            rdate = line.split(' ')[1].split('.')
            rtime = line.split(' ')[3].split(':')
            runtime = datetime(2000+int(rdate[2]),int(rdate[1]),int(rdate[0]),int(rtime[0]),int(rtime[1]),int(rtime[2])) - datetime(1904,1,1,9,0,0,0)
            lvtime = 24*60*60*float(runtime.days) + float(runtime.seconds/86400.00000)
            tmstamp = 24*60*60*runtime.days + runtime.seconds	
            print rdate, rtime, runtime, runtime.seconds, lvtime, tmstamp

        #Only looks at lines with data in them
        if line.count(',') > 3:
            event += 1 #increments the event count
	    if event % 4 == 1:
	    	evttime = float(line.split('\t')[0])
		if evttime > tmstamp: tmstamp = evttime
            #Converts Data line to array
            full_event = [float(x) for x in line.replace('\r\t','').split('\t')[-1].split(',')]
	    #print full_event

            if event % 4000 == 0: print event/4 #Prints status
            #Converts to electrons if scale is not equal to 1
            if scale != 1: event_data += [x*192000.0/full_event[-1] for x in full_event[12:-1]]
            
            #Add APV data to event_data
            else: 
		#if event % 4 == 0: event_data += full_event[11:-2]
		#else: event_data += full_event[12:-1]
		event_data += full_event[12:-1]

	    apv_event = event_data[(region+1)/4*128:(1+(region+1)/4)*128]
            #Once you have all 4 APVs for one event...
            if event % 4 == 0:
                #Fill TProfile with all 512 elements/channels of the event_data
		#avgevt = sum(event_data)/float(len(event_data))
		avgevt = sum(apv_event)/float(len(apv_event))
		rmssum = 0
                for chan in range(len(apv_event)): rmssum += (apv_event[chan] - avgevt)*(apv_event[chan] - avgevt)		
		if (rmssum/float(len(apv_event))) > 100:
			NoisyEvts += 1
		else:	
                	for chan in range(len(event_data)):
                    		#Fills the Pedestal with channel values
                    		if Pedestal2 == None: Ped_Data.Fill(chan, event_data[chan])
                    		#Option if you want to compare pedestals, not important
                    		else: Ped_Data.Fill(chan, event_data[chan]-Pedestal2.GetBinContent(chan+1))
                    		#stp[0] = int(chan)
                    		#ped[0] = event_data[chan]
                    		#RTree.Fill()
		    		if (chan >= 0) and (chan<128): APV0_Data.Fill(chan,event_data[chan])
		    		if (chan >= 128) and (chan<256): APV1_Data.Fill(chan%128,event_data[chan])
		    		if (chan >= 256) and (chan<384): APV2_Data.Fill(chan%128,event_data[chan])
		    		if (chan >= 384) and (chan<512): APV3_Data.Fill(chan%128,event_data[chan])

		Ped_CM.Fill(rmssum/float(len(apv_event)))
                event_data = []

    ped_file.close()

    #Pedestal = Ped_Data.ProfileX(title)

    print "Noisy Events: ",NoisyEvts
    PedNsyEvts[0] = NoisyEvts

    for i in xrange(512):
	Noise_Region.Fill(i/32, Ped_Data.GetBinError(i+1))
	stp[0] = i
        ped[0] = Ped_Data.GetBinContent(i)
        noise[0] = Ped_Data.GetBinError(i)*R.sqrt(Ped_Data.GetBinEntries(i))
        RTree.Fill()

    pedarr = []
    for i in xrange(512): pedarr.append(Ped_Data.GetBinContent(i+1))
    for i in xrange(512): print i, pedarr[i]
	
    #Saves the Pedestal to the RootFile
    if RFile_name != '':
        RFile = R.TFile(RFile_name,'UPDATE')
        PedStartTime[0] = tmstamp
        PedStartTime.Write("PedStartTime")
	#PedStartTemp[0] = -99.0
	#PedStartTemp.Write("PedStartTemp")
        Ped_Data.Write()
	Ped_CM.Write()
	PedNsyEvts.Write("PedNoisyEvts")
	APV0_Data.Write()
	APV1_Data.Write()
	APV2_Data.Write()
	APV3_Data.Write()
	Noise_Region.Write()
        RTree.Write()

        #Pedestal.Write()
        RFile.Close()

    #Returns Pedestal for future use
    return Ped_Data

def get_preped3(file_name, title, region, RFile_name = '', T_Data=0, scale = 1, Pedestal2 = None):

    #Sets whether you want results in ADC or Electrons
    print 'SCALE:',scale
    
    #Opens data file with pedestal information
    if file_name.find("Raw_Data_") == -1: exefile = False
    else: exefile = True
    print "Old file: ", exefile
    ped_file = open(file_name,'r')
    
    #Creates the TProfile which stores the information about channel averages and noise
    Ped_Data = R.TProfile('Ped Data ' + title,'Ped Data ' + title,512,0,512)
    Ped_Data.Sumw2() #Calculates TRUE average
    Ped_Data.SetOption('colz')
    Ped_Data0 = R.TProfile('Ped Data0 ' + title,'Ped Data ' + title,512,0,512)
    Ped_Data0.Sumw2() #Calculates TRUE average
    Ped_Data0.SetOption('colz')
    Ped_Data1 = R.TProfile('Ped Data1 ' + title,'Ped Data ' + title,512,0,512)
    Ped_Data1.Sumw2() #Calculates TRUE average
    Ped_Data1.SetOption('colz')
    Ped_Data2 = R.TProfile('Ped Data2 ' + title,'Ped Data ' + title,512,0,512)
    Ped_Data2.Sumw2() #Calculates TRUE average
    Ped_Data2.SetOption('colz')
    Ped_CM = R.TH1F('PrepedCM','Preped CM',512,0,512)


    APV0_Data = R.TH2I('APV0','APV0',128,0,128,100,0,100)
    APV1_Data = R.TH2I('APV1','APV1',128,0,128,100,0,100)
    APV2_Data = R.TH2I('APV2','APV2',128,0,128,100,0,100)
    APV3_Data = R.TH2I('APV3','APV3',128,0,128,100,0,100)
    APV0_Data.SetOption('colz')
    APV1_Data.SetOption('colz')
    APV2_Data.SetOption('colz')
    APV3_Data.SetOption('colz')
    Noise_Region = R.TProfile('RegNoise','Noise by Region',16,0,16)

    #Creates TObject to store time
    PedStartTime = R.TVectorF(1)
    PedStartTemp = R.TVectorF(1)
    PedNsyEvts = R.TVectorF(1)

    stp = array('i',[0])
    ped = array('f',[0.])
    noise = array('f',[0.])
    ped0 = array('f',[0.])
    noise0 = array('f',[0.])
    ped1 = array('f',[0.])
    noise1 = array('f',[0.])
    ped2 = array('f',[0.])
    noise2 = array('f',[0.])

    RTree = R.TTree('ppd','Ped_Data')
    RTree.Branch('stp',stp,'stp/I')
    RTree.Branch('ped',ped,'ped/F')
    RTree.Branch('noise',noise,'noise/F')
    RTree.Branch('ped0',ped0,'ped0/F')
    RTree.Branch('noise0',noise0,'noise0/F')
    RTree.Branch('ped1',ped1,'ped1/F')
    RTree.Branch('noise1',noise1,'noise1/F')
    RTree.Branch('ped2',ped2,'ped2/F')
    RTree.Branch('noise2',noise2,'noise2/F')

    #Reads in Data and stores in TProfile hi
    event_data = [[],[],[]] #stores data from 512 channels of 1 event
    event_data0 = []
    event_data1 = []
    event_data2 = []
    event = 0 #Counts the number of events
    NoisyEvts = 0 #Counts the number of events
    tmstamp = 0

    for line in ped_file:
        #Read out time from file
        if line[0:4] == 'Date':
            rdate = line.split(' ')[1].split('.')
            rtime = line.split(' ')[3].split(':')
            runtime = datetime(2000+int(rdate[2]),int(rdate[1]),int(rdate[0]),int(rtime[0]),int(rtime[1]),int(rtime[2])) - datetime(1904,1,1,9,0,0,0)
            lvtime = 24*60*60*float(runtime.days) + float(runtime.seconds/86400.00000)
            tmstamp = 24*60*60*runtime.days + runtime.seconds	
            print rdate, rtime, runtime, runtime.seconds, lvtime, tmstamp

        #Only looks at lines with data in them
        if line.count(',') > 3:
            event += 1 #increments the event count
	    if event % 4 == 1:
	    	evttime = float(line.split('\t')[0])
		if evttime > tmstamp: tmstamp = evttime
            #Converts Data line to array
            full_event = [float(x) for x in line.replace('\r\t','').split('\t')[-1].split(',')]
	    #print full_event

            if event % 4000 == 0: print event/4 #Prints status
            #Converts to electrons if scale is not equal to 1
            if scale != 1: event_data += [x*192000.0/full_event[-1] for x in full_event[12:-1]]
            
            #Add APV data to event_data
            else: 
		#event_data += full_event[12:-1]
		#print len(event_data),"A",event_data[0:128],"B", event_data[140:268],"C", event_data[280:408],"D",event_data[409:536],"E",event_data[548:676],"F",event_data[688:816],"G",event_data[817:944],"H",event_data[956:1084],"I",event_data[1096:1225],"J",event_data[1226:1352],"K",event_data[1364:1492],"L",event_data[1504:1636]
		event_data0+=(full_event[12:140])
		event_data1+=(full_event[152:280])
		event_data2+=(full_event[292:420])
		event_data = [event_data0, event_data1, event_data2]
		#print len(full_event),len(event_data0),full_event[12], full_event[152], full_event[292], event_data0[0], event_data1[0], event_data2[0]
		#print event_data0, event_data1, event_data2
		#print len(event_data)
		#print event_data0[0:2], event_data[0][0:2], event_data1[0:2], event_data[1][0:2]
	
            
	    apv_event = [event_data[0][(region+1)/4*128:(1+(region+1)/4)*128],event_data[1][(region+1)/4*128:(1+(region+1)/4)*128],event_data[2][(region+1)/4*128:(1+(region+1)/4)*128]]
            #Once you have all 4 APVs for one event...
            if event % 4 == 0:
		#print len(event_data[0])
		#print apv_event[0]
                #Fill TProfile with all 512 elements/channels of the event_data
		#avgevt = sum(event_data)/float(len(event_data))
		#print apv_event[0]
		avgevt = sum(apv_event[0])/float(len(apv_event[0]))
		rmssum = 0
                for chan in range(len(apv_event)): rmssum += (apv_event[0][chan] - avgevt)*(apv_event[0][chan] - avgevt)		
		if (rmssum/float(len(apv_event))) > 100:
			NoisyEvts += 1
		else:	
                	for chan in range(len(event_data[0])):
                    		#Fills the Pedestal with channel values
                    		if Pedestal2 == None: 
					Ped_Data.Fill(chan, event_data[0][chan])
					Ped_Data.Fill(chan, event_data[1][chan])
					Ped_Data.Fill(chan, event_data[2][chan])
					Ped_Data0.Fill(chan, event_data[0][chan])
					Ped_Data1.Fill(chan, event_data[1][chan])
					Ped_Data2.Fill(chan, event_data[2][chan])
					#print "A",event_data[0][chan], event_data[1][chan], event_data[2][chan]
                    		#Option if you want to compare pedestals, not important
                    		else: Ped_Data.Fill(chan, event_data[chan]-Pedestal2.GetBinContent(chan+1))
                    		#stp[0] = int(chan)
                    		#ped[0] = event_data[chan]
                    		#RTree.Fill()
		    		if (chan >= 0) and (chan<128): APV0_Data.Fill(chan,event_data[0][chan])
		    		if (chan >= 128) and (chan<256): APV1_Data.Fill(chan%128,event_data[0][chan])
		    		if (chan >= 256) and (chan<384): APV2_Data.Fill(chan%128,event_data[0][chan])
		    		if (chan >= 384) and (chan<512): APV3_Data.Fill(chan%128,event_data[0][chan])

		Ped_CM.Fill(rmssum/float(len(apv_event)))
                #event_data = []
    		event_data0 = []
		event_data1 = []
		event_data2 = []

    ped_file.close()

    #Pedestal = Ped_Data.ProfileX(title)

    print "Noisy Events: ",NoisyEvts
    PedNsyEvts[0] = NoisyEvts

    for i in xrange(512):
	Noise_Region.Fill(i/32, Ped_Data.GetBinError(i+1))
	stp[0] = i
        ped[0] = Ped_Data.GetBinContent(i)
        noise[0] = Ped_Data.GetBinError(i)*R.sqrt(Ped_Data0.GetBinEntries(i))
        ped0[0] = Ped_Data0.GetBinContent(i)
        noise0[0] = Ped_Data0.GetBinError(i)*R.sqrt(Ped_Data0.GetBinEntries(i))
        ped1[0] = Ped_Data1.GetBinContent(i)
        noise1[0] = Ped_Data1.GetBinError(i)*R.sqrt(Ped_Data1.GetBinEntries(i))
        ped2[0] = Ped_Data2.GetBinContent(i)
        noise2[0] = Ped_Data2.GetBinError(i)*R.sqrt(Ped_Data2.GetBinEntries(i))
        RTree.Fill()
	
    #Saves the Pedestal to the RootFile
    if RFile_name != '':
        RFile = R.TFile(RFile_name,'UPDATE')
        PedStartTime[0] = tmstamp
        PedStartTime.Write("PedStartTime")
	#PedStartTemp[0] = -99.0
	#PedStartTemp.Write("PedStartTemp")
        Ped_Data.Write()
        Ped_Data0.Write()
        Ped_Data1.Write()
        Ped_Data2.Write()
	Ped_CM.Write()
	PedNsyEvts.Write("PedNoisyEvts")
	APV0_Data.Write()
	APV1_Data.Write()
	APV2_Data.Write()
	APV3_Data.Write()
	Noise_Region.Write()
        RTree.Write()

        #Pedestal.Write()
        RFile.Close()

    #Returns Pedestal for future use
    return Ped_Data

def get_pedestal(file_name, region, PrePed, title, RFile_name, scale = 1):

    file = open(file_name, 'r')
    
    Ped_Data = R.TProfile('Ped Data ' + title,'Ped Data ' + title,512,0,512)
    Ped_Data.Sumw2()
    Ped_Data.SetOption('colz')
    
    Total_Noise = R.TH1F('Noise ' + title, 'Noise ' + title, 40*scale, -10*scale, 10*scale)
    Total_Noise.Sumw2()
    Total_Noise.SetOption('hist')

    stp = array('i',[0])
    ppd = array('f',[0.])
    ped = array('f',[0.])
    noise = array('f',[0.])

    RTree = R.TTree('pd','Ped_Data')
    RTree.Branch('stp',stp,'stp/I')
    RTree.Branch('ppd',ppd,'ppd/F')
    RTree.Branch('ped',ped,'ped/F')
    RTree.Branch('noise',noise,'noise/F')

    event_data = []
    event = 0
    for line in file:
        if line.count(',') > 3:
            event += 1
            if event % 4000 == 0: print event/4
            full_event = [float(x) for x in line.replace('\r\t','').split('\t')[-1].split(',')]
            if scale != 1: event_data += [x*192000.0/full_event[-1] for x in full_event[12:-1]]
            else: event_data += full_event[12:-1]
            if event % 4 == 0:
                subtracted_event = [event_data[i] - PrePed.GetBinContent(i+1) for i in range(512)]
                #print subtracted_event
                max_chan = subtracted_event.index(max(subtracted_event[32*(region+1):32*(region+2)]))
                for chan in range(len(event_data)):
                    if chan < max_chan - 1 or chan > max_chan + 1:
                        Ped_Data.Fill(chan, event_data[chan])
                        if chan >= 32 * (region +1) and chan < 32 * (region +2): Total_Noise.Fill(subtracted_event[chan])
			#stp[0] = chan
			#ped[0] = event_data[chan]
			#RTree.Fill()
                event_data = []
    file.close()

    for i in xrange(512):
	stp[0] = i
	ppd[0] = PrePed.GetBinContent(i)
	ped[0] = Ped_Data.GetBinContent(i)
	noise[0] = Ped_Data.GetBinError(i)*R.sqrt(Ped_Data.GetBinEntries(i))
	RTree.Fill()


    if RFile_name != '':
        RFile = R.TFile(RFile_name,'UPDATE')
        Ped_Data.Write()
        Total_Noise.Write()
	RTree.Write()
        RFile.Close()

    return Ped_Data

def get_pedestal3(file_name, region, PrePed, title, RFile_name, scale = 1):

    file = open(file_name, 'r')
    
    Ped_Data = R.TProfile('Ped Data ' + title,'Ped Data ' + title,512,0,512)
    Ped_Data.Sumw2()
    Ped_Data.SetOption('colz')
    Ped_Data0 = R.TProfile('Ped Data0 ' + title,'Ped Data ' + title,512,0,512)
    Ped_Data0.Sumw2()
    Ped_Data0.SetOption('colz')
    Ped_Data1 = R.TProfile('Ped Data1 ' + title,'Ped Data ' + title,512,0,512)
    Ped_Data1.Sumw2()
    Ped_Data1.SetOption('colz')
    Ped_Data2 = R.TProfile('Ped Data2 ' + title,'Ped Data ' + title,512,0,512)
    Ped_Data2.Sumw2()
    Ped_Data2.SetOption('colz')
    
    Total_Noise = R.TH1F('Noise ' + title, 'Noise ' + title, 40*scale, -10*scale, 10*scale)
    Total_Noise.Sumw2()
    Total_Noise.SetOption('hist')

    stp = array('i',[0])
    ped = array('f',[0.])
    noise = array('f',[0.])
    ped0 = array('f',[0.])
    noise0 = array('f',[0.])
    ped1 = array('f',[0.])
    noise1 = array('f',[0.])
    ped2 = array('f',[0.])
    noise2 = array('f',[0.])

    RTree = R.TTree('ppd','Ped_Data')
    RTree.Branch('stp',stp,'stp/I')
    RTree.Branch('ped',ped,'ped/F')
    RTree.Branch('noise',noise,'noise/F')
    RTree.Branch('ped0',ped0,'ped0/F')
    RTree.Branch('noise0',noise0,'noise0/F')
    RTree.Branch('ped1',ped1,'ped1/F')
    RTree.Branch('noise1',noise1,'noise1/F')
    RTree.Branch('ped2',ped2,'ped2/F')
    RTree.Branch('noise2',noise2,'noise2/F')

    event_data = []
    event_data0 = []
    event_data1 = []
    event_data2 = []
    event = 0
    for line in file:
        if line.count(',') > 3:
            event += 1
            if event % 4000 == 0: print event/4
	    #print event
            full_event = [float(x) for x in line.replace('\r\t','').split('\t')[-1].split(',')]
            if scale != 1: event_data += [x*192000.0/full_event[-1] for x in full_event[12:-1]]
            else: 
		event_data0+=(full_event[12:140])
		event_data1+=(full_event[152:280])
		event_data2+=(full_event[292:420])
		event_data = [event_data0, event_data1, event_data2]
		#event_data += full_event[12:-1]
            if event % 4 == 0:
		#x1 = [event_data[0][i] - PrePed.GetBinContent(i+1) for i in range(512)]
		#x2 = [event_data[1][i] - PrePed.GetBinContent(i+1) for i in range(512)]
		#x3 = [event_data[2][i] - PrePed.GetBinContent(i+1) for i in range(512)]
		#subtracted_event = [x1,x1,x1]
                subtracted_event = [[event_data[0][i] - PrePed.GetBinContent(i+1) for i in range(512)],[event_data[1][j] - PrePed.GetBinContent(j+1) for j in range(512)],[event_data[2][k] - PrePed.GetBinContent(k+1) for k in range(512)]]
                #print subtracted_event
		#max1 = subtracted_event[0].index(max(subtracted_event[0][32*(region+1):32*(region+2)]))
		#max2 = subtracted_event[1].index(max(subtracted_event[1][32*(region+1):32*(region+2)]))
		#max3 = subtracted_event[2].index(max(subtracted_event[2][32*(region+1):32*(region+2)]))
		#max_chan = [max1, max1, max1]
                max_chan = [subtracted_event[0].index(max(subtracted_event[0][32*(region+1):32*(region+2)])),subtracted_event[1].index(max(subtracted_event[1][32*(region+1):32*(region+2)])),subtracted_event[2].index(max(subtracted_event[2][32*(region+1):32*(region+2)]))]
                for chan in range(len(event_data[0])):
                    if chan < max_chan[0] - 1 or chan > max_chan[0] + 1:
			Ped_Data.Fill(chan, event_data[0][chan])
			Ped_Data0.Fill(chan, event_data[0][chan])
                    if chan < max_chan[1] - 1 or chan > max_chan[1] + 1:
			Ped_Data.Fill(chan, event_data[1][chan])
			Ped_Data1.Fill(chan, event_data[1][chan])
                    if chan < max_chan[2] - 1 or chan > max_chan[2] + 1:
			Ped_Data2.Fill(chan, event_data[2][chan])
			Ped_Data.Fill(chan, event_data[2][chan])

                        #Ped_Data.Fill(chan, event_data[chan])
                        if chan >= 32 * (region +1) and chan < 32 * (region +2): 
				Total_Noise.Fill(subtracted_event[0][chan])
				Total_Noise.Fill(subtracted_event[1][chan])
				Total_Noise.Fill(subtracted_event[2][chan])
			#stp[0] = chan
			#ped[0] = event_data[chan]
			#RTree.Fill()
                event_data0 = []
                event_data1 = []
                event_data2 = []
                event_data = []
    file.close()

    for i in xrange(512):
	stp[0] = i
        ped[0] = Ped_Data.GetBinContent(i)
        noise[0] = Ped_Data.GetBinError(i)*R.sqrt(Ped_Data0.GetBinEntries(i))
        ped0[0] = Ped_Data0.GetBinContent(i)
        noise0[0] = Ped_Data0.GetBinError(i)*R.sqrt(Ped_Data0.GetBinEntries(i))
        ped1[0] = Ped_Data1.GetBinContent(i)
        noise1[0] = Ped_Data1.GetBinError(i)*R.sqrt(Ped_Data1.GetBinEntries(i))
        ped2[0] = Ped_Data2.GetBinContent(i)
        noise2[0] = Ped_Data2.GetBinError(i)*R.sqrt(Ped_Data2.GetBinEntries(i))
	RTree.Fill()


    if RFile_name != '':
        RFile = R.TFile(RFile_name,'UPDATE')
        Ped_Data.Write()
        Ped_Data0.Write()
        Ped_Data1.Write()
        Ped_Data2.Write()
        Total_Noise.Write()
	RTree.Write()
        RFile.Close()

    return Ped_Data

def find_bad_chans(file_name, region, Ped, title, RFile_name, scale = 1, extra = None):

    if extra == None: extra = 'Region '+ str(13-(region))
    file = open(file_name, 'r')

    Sig_Data = R.TProfile(extra + ' Data',extra + ' Data',32, 0, 32)
    Sig_Data.Sumw2()
    Sig_Data.SetOption('colz')
    
    Sig_Data2 = R.TH2D(extra + ' Data2',extra + ' Data2',32, 0, 32, 150, -75.5*scale, 74.5*scale)
    Sig_Data2.Sumw2()
    Sig_Data2.SetOption('colz')
    
    good = R.TH1D('Good','Good',150, -75.5*scale,74.5*scale)
    bad = R.TH1D('Bad','Bad',150, -75.5*scale,74.5*scale)
    bad2 = R.TH1D('Bad2','Bad2',150, -75.5*scale,74.5*scale)
    
    good.Sumw2()
    bad.Sumw2()
    bad2.Sumw2()
    
    

    event_data = []
    event = 0
    for line in file:
        if line.count(',') > 3:
            event += 1
            if event % 4000 == 0: print event/4
            
            full_event = [float(x) for x in line.replace('\r\t','').split('\t')[-1].split(',')]
            if scale != 1: event_data += [x*192000.0/full_event[-1] for x in full_event[12:-1]]
            else: event_data += full_event[12:-1]
            
            if event % 4 == 0:
                subtracted_event = [event_data[i] - Ped.GetBinContent(i+1) for i in range(512)]
                reg_event = subtracted_event[32*(region+1):32*(region+2)]
                for chan in range(len(reg_event)):
                    Sig_Data.Fill(chan, reg_event[chan])
                    Sig_Data2.Fill(chan, reg_event[chan])
                event_data = []

    dict = []
    bad_chans = []
    for i in range(32):
        if Sig_Data.GetBinContent(i+1) < (0)*scale:
            if i not in bad_chans: bad_chans.append(i)
            if i+1 not in bad_chans and i+1 < 32: bad_chans.append(i+1)
            if i-1 not in bad_chans and i-1 > -1: bad_chans.append(i-1)


    if RFile_name != '':
        RFile = R.TFile(RFile_name,'UPDATE')
        #Sig_Data.Write()
        #Sig_Data2.Write()
        #prof.Write()
        #Pedestal.Write()
        RFile.Close()
    print bad_chans
    return bad_chans

def get_signal(file_name, region, Ped, title, RFile_name, bad_chans, RunNum, scale = 1, T_Array=0, stripstart=0, stripend=31, cut=0, extra = None):

    print "strips ", stripstart, stripend
    if extra == None: extra = 'R'+str(13-(region))
    file = open(file_name, 'r')    

    runno = array('i', [0])
    eventno = array('i', [0])
    hit_strip = array('i', [0])
    clust_charge = array ('f', [0.])
    strip_charge = array ('f', [0.])
    #SR1_charge = array ('f', [0.])
    #SR2_charge = array ('f', [0.])
    #SL1_charge = array ('f', [0.])
    #SL2_charge = array ('f', [0.])
    R1 = array ('f', [0.])
    R2 = array ('f', [0.])
    L1 = array ('f', [0.])
    L2 = array ('f', [0.])
    eta = array ('f', [0.])
    CM_noise = array ('f', [0.])

    sig_noise = array ('f', [0.])
    soft_evt = array ('i', [0])
    T_Chuck = array ('f', [0.])


    RhdFile_name = RFile_name[:-5] + "_hd.root"
    print RhdFile_name
    RhdFile = R.TFile(RhdFile_name,'RECREATE')
    
    RTree = R.TTree('hits', 'Hit Data')
    RTree.Branch('runno',runno,'runno/I')
    RTree.Branch('eventno',eventno,'eventno/I')
    RTree.Branch('hit_strip',hit_strip,'hit_strip/I')
    RTree.Branch('clust_charge',clust_charge,'clust_charge/F')
    RTree.Branch('strip_charge',strip_charge,'strip_charge/F')
    #RTree.Branch('SR1_charge',SR1_charge,'SR1_charge/F')
    #RTree.Branch('SR2_charge',SR2_charge,'SR2_charge/F')
    #RTree.Branch('SL1_charge',SL1_charge,'SL1_charge/F')
    #RTree.Branch('SL2_charge',SL2_charge,'SL2_charge/F')
    RTree.Branch('R1',R1,'R1/F')
    RTree.Branch('R2',R2,'R2/F')
    RTree.Branch('L1',L1,'L1/F')
    RTree.Branch('L2',L2,'L2/F')
    RTree.Branch('eta',eta,'eta/F')
    RTree.Branch('CM_noise',CM_noise,'CM_noise/F')
    RTree.Branch('sig_noise',sig_noise,'sig_noise/F')
    RTree.Branch('soft_evt',soft_evt,'soft_evt/I')
    RTree.Branch('T_Chuck',T_Chuck,'T_Chuck/F')

    if RFile_name != '':
        RFile = R.TFile(RFile_name,'UPDATE')

    CMs = R.TH1D('CMs '+extra,'CMs '+extra, 20, -5*scale, 5*scale)
    CMs.Sumw2()
    CMs.SetOption('hist')
    
    Sig_Data = R.TProfile(extra + ' Data',extra + ' Data',32, 0, 32)
    Sig_Data.Sumw2()
    Sig_Data.SetOption('colz')
    Hit_Data = R.TH1D("HitStrip", "Hit Strip", 32, 0, 32)
    Hit_Data.Sumw2()
    Hit_Data.SetOption('hist')

    h_name_fine_bin = extra + ' Signal_' + '1000' + 'Bins'
    h_name_fine_bin_clust = extra + ' Signal_' + '1000' + 'Bins_clust'
    h_name_coarse_bin_clust = extra + ' Signal_' + '100' + 'Bins_clust'
    SignalHist1 = R.TH1D(h_name_fine_bin, h_name_fine_bin, 1000, 0, 100*scale)
    SignalHist1.Sumw2()
    SignalHist1.SetOption('hist')
    SignalHist2 = R.TH1D(h_name_fine_bin_clust, h_name_fine_bin_clust, 1000, 0, 100*scale)
    SignalHist2.Sumw2()
    SignalHist2.SetOption('hist')
    SignalHist3 = R.TH1D(h_name_coarse_bin_clust, h_name_coarse_bin_clust, 100, 0, 100*scale)
    SignalHist3.Sumw2()
    SignalHist3.SetOption('hist')
    EtaHist = R.TH1D("Eta","Eta", 120, -0.1, 1.1)
    EtaHist.Sumw2()
    EtaHist.SetOption('hist')
    HitProf = R.TProfile("HitProf", "Hit Profile", 7, 0, 7)


    #Creates TObject to store time
    StartTime = R.TVectorF(1)
    StartTemp = R.TVectorF(1)
    NoisyEvts = R.TVectorF(1)
    SoftEvts = R.TVectorF(1)
    NoiseHits = R.TVectorF(1)
    EtaPct = R.TVectorF(1)
   
    runno[0] = RunNum
    event_data = []
    StartTemp[0] = -99.0
    event = 0
    NbadChans = 0
    Nnoisehits = 0
    NsoftSignal = 0
    NnoisyEvts = 0
    NgoodEvts = 0
    Tindex = 0
    tmstamp = 0
    mideta = 0
    toteta = 0
    hit1 = hit2 = hit3 = 0

    print bad_chans
    for line in file:
        #Read out time from file
        if line[0:4] == 'Date':
            rdate = line.split(' ')[1].split('.')
            rtime = line.split(' ')[3].split(':')
            runtime = datetime(2000+int(rdate[2]),int(rdate[1]),int(rdate[0]),int(rtime[0]),int(rtime[1]),int(rtime[2])) - datetime(1904,1,1,0,0,0,0)
            lvtime = 24*60*60*float(runtime.days) + float(runtime.seconds/86400.00000)
            tmstamp = 24*60*60*runtime.days + runtime.seconds
            print rdate, rtime, runtime, runtime.days, runtime.seconds, tmstamp

        if line.count(',') > 3:
            event += 1
	    if event % 4 == 1:
	    	evttime = float(line.split('\t')[0])
		if evttime > tmstamp: tmstamp = evttime
		tca = get_temp (T_Array, tmstamp, Tindex)
		T_Chuck[0] = tca[0]
		Tindex = tca[1]
		if StartTemp[0] < 90: StartTemp[0] = T_Chuck[0]

            if event % 4000 == 0: print event/4
            
            full_event = [float(x) for x in line.replace('\r\t','').split('\t')[-1].split(',')]
            if scale != 1: event_data += [x*192000.0/full_event[-1] for x in full_event[12:-1]]
            else: event_data += full_event[12:-1]
            
            if event % 4 == 0:
		eventno[0] = event/4
                subtracted_event = [event_data[i] - Ped.GetBinContent(i+1) for i in range(512)]
                apv_event = subtracted_event[(region+1)/4*128:(1+(region+1)/4)*128]
                reg_event = subtracted_event[32*(region+1):32*(region+2)]
                
                for chan in range(len(reg_event)):
                    Sig_Data.Fill(chan, reg_event[chan])

                #print max(subtracted_event), subtracted_event.index(max(subtracted_event))/32 - 1, max(reg_event), reg_event.index(max(reg_event))
                #raw_input('')
                
                eventSN = []
                for i in range(512):
                    if Ped.GetBinError(i+1) == 0: eventSN.append(0)
                    else: eventSN.append( subtracted_event[i]/float(Ped.GetBinError(i+1)*R.sqrt(Ped.GetBinEntries(i+1))) )
            
            
                apv = (region+1)/4
                apvSN = eventSN[(region+1)/4*128:(1+(region+1)/4)*128]
                regSN = eventSN[32*(region+1):32*(region+2)]

		#for i in xrange(len(regSN)):
		#	if regSN[i] > 2.75: hit3 +=1
		#	if regSN[i] > 2.5: hit2 += 1
		#	if regSN[i] > 2.25: hit1 += 1
                
                chan_nums = [i for i in range(32)]
                
                good_regevt = [reg_event[i] for i in range(32) if i not in bad_chans]
                good_regSN = [regSN[i] for i in range(32) if i not in bad_chans]
                goodchan_nums = [chan_nums[i] for i in range(32) if i not in bad_chans]
                
                #Takes max signal to noise
                #good_max_reg_chan = good_regSN.index(max(good_regSN))
                good_max_reg_chan = good_regevt.index(max(good_regevt))
                max_reg_chan = goodchan_nums[good_max_reg_chan]
                
                if max_reg_chan in bad_chans: print max_reg_chan
                max_apv_chan = ((region+1)%4)*32 + max_reg_chan
                max_all_chan = (region+1)*32 + max_reg_chan
                hit_strip[0] = max_reg_chan
		Noisehit = False
                if max_reg_chan < stripstart or max_reg_chan > stripend:
                       	Hit_Data.Fill(max_reg_chan)
			Noisehit = True
			Nnoisehits += 1

                #max_reg_chan = reg_event.index(max(reg_event))
                #max_apv_chan = ((region+1)%4)*32 + max_reg_chan
                #max_all_chan = (region+1)*32 + max_reg_chan
                
                #CM = sum(apv_event) - apv_event[max_apv_chan]
                #count = 127.0

		#Loop over APV events and subtract off neighbors of the hit strip and bad/noisy channels
		#for i in xrange(128):
                #	if abs(max_apv_chan - 1) == 1:
                #    		CM -= apv_event[i]
                #    		count -= 1
                #	if ((128*apv) + i) in bad_chans:
		#		#print "removing bad_chan", i, apv_event[i]
                #    		CM -= apv_event[i]
                #    		count -= 1

                CM = sum(reg_event) - apv_event[max_apv_chan]
                count = 31.0

		#Loop over APV events and subtract off neighbors of the hit strip and bad/noisy channels
                if ((max_reg_chan - 1) >=0) and ((max_reg_chan - 1) not in bad_chans):
                    	CM -= reg_event[max_reg_chan-1]
                    	count -= 1
                if ((max_reg_chan + 1) <32) and ((max_reg_chan + 1) not in bad_chans):
                    	CM -= reg_event[max_reg_chan+1]
                    	count -= 1

		for i in xrange(32):
                	if i in bad_chans:
				#print "removing bad_chan", i, apv_event[i]
                    		CM -= reg_event[i]
                    		count -= 1
                
                CM /= count
                CMs.Fill(CM)
                CM_noise[0] = CM
		NoisyEvt = False
		if abs(CM) > 5:	
			NoisyEvt = True
                	NnoisyEvts+=1

                if max_reg_chan in bad_chans:
                    event_data = []
                    NbadChans+=1
                    continue
            
                #if( apv_event[max_apv_chan] > 10): print apv_event[max_apv_chan], CM
                    
                #Fill unclustered histogram and tree brances
                seed_signal = apv_event[max_apv_chan] - CM
		total_signal = seed_signal
                strip_charge[0] = seed_signal

		#If hit is not on edges record entire 4 strip cluster
		#Possibly a bias if significant number of apv_evt[chan-1] = apv_evt[chan+1]
		wholecluster = False
		#print "max_reg_chan", max_reg_chan
		if (max_reg_chan > 0) and (max_reg_chan < 31): 
		   if apv_event[max_apv_chan+1] > apv_event[max_apv_chan-1]:
			if ((max_reg_chan + 2) < 32) and ((max_reg_chan - 1) > -1):
				L1[0] = apv_event[max_apv_chan] - CM
				R1[0] = apv_event[max_apv_chan+1] - CM
				L2[0] = apv_event[max_apv_chan-1] - CM
				R2[0] = apv_event[max_apv_chan+2] - CM
				wholecluster = True
		   else:
			if ((max_reg_chan + 1) < 32) and ((max_reg_chan - 2) > -1):
				L1[0] = apv_event[max_apv_chan-1] - CM
				R1[0] = apv_event[max_apv_chan] - CM
				L2[0] = apv_event[max_apv_chan-2] - CM
				R2[0] = apv_event[max_apv_chan+1] - CM
				wholecluster = True
		   if apv_event[max_apv_chan+1] == apv_event[max_apv_chan-1]: print "Left & Right neighbors equal charge!"


                #Do clustering and fill histograms. Change from 2 -> 1 times the noise to get counted in cluster
		#Now just add neighbors without doing a cut
		HitProf.Fill(3,apv_event[max_apv_chan]-CM)
                if (max_reg_chan + 1) < 32:
                    total_signal += apv_event[max_apv_chan+1] - CM
		    HitProf.Fill(4,apv_event[max_apv_chan+1]-CM)		
                    #if (apv_event[max_apv_chan+1]-CM) > 1*Ped.GetBinError(max_all_chan + 1 + 1)*R.sqrt(Ped.GetBinEntries(max_all_chan + 1 + 1)): total_signal += apv_event[max_apv_chan+1] - CM
                    #SR1_charge[0] = apv_event[max_apv_chan+1] - CM
                    #if (max_reg_chan + 2) < 32:  SR2_charge[0] = apv_event[max_apv_chan+2] - CM
                if (max_reg_chan - 1) > -1:
                    total_signal += apv_event[max_apv_chan-1] - CM
		    HitProf.Fill(2,apv_event[max_apv_chan-1]-CM)		
                    #if (apv_event[max_apv_chan-1]-CM) > 1*Ped.GetBinError(max_all_chan - 1 + 1)*R.sqrt(Ped.GetBinEntries(max_all_chan - 1 + 1)): total_signal += apv_event[max_apv_chan-1] - CM
                    #SL1_charge[0] = apv_event[max_apv_chan-1] - CM
                    #if (max_reg_chan - 2) > -1:  SL2_charge[0] = apv_event[max_apv_chan-2] - CM
                if (max_reg_chan - 2) > -1:  HitProf.Fill(1, apv_event[max_apv_chan-2]-CM)
                if (max_reg_chan + 2) < 32:  HitProf.Fill(5, apv_event[max_apv_chan+2]-CM)
                if (max_reg_chan - 3) > -1:  HitProf.Fill(1, apv_event[max_apv_chan-3]-CM)
                if (max_reg_chan + 3) < 32:  HitProf.Fill(5, apv_event[max_apv_chan+3]-CM)
                     


                clust_charge[0] = total_signal

                #Mark soft events (less than 3x noise) in tree (was previously 5x noise)
                soft_evt[0] = 0
		#if Ped.GetBinError(max_all_chan + 1)*R.sqrt(Ped.GetBinEntries(max_all_chan + 1)) == 0:
		#	print Ped.GetBinError(max_all_chan + 1), Ped.GetBinEntries(max_all_chan + 1), max_all_chan
		#	sig_noise[0] = 0
                #else: sig_noise[0] = float(reg_event[max_reg_chan])/(Ped.GetBinError(max_all_chan + 1)*R.sqrt(Ped.GetBinEntries(max_all_chan + 1)))
                sig_noise[0] = float(reg_event[max_reg_chan])/(Ped.GetBinError(max_all_chan + 1)*R.sqrt(Ped.GetBinEntries(max_all_chan + 1)))
                if (reg_event[max_reg_chan]-CM) < cut*Ped.GetBinError(max_all_chan + 1)*R.sqrt(Ped.GetBinEntries(max_all_chan + 1)):
                    soft_evt[0] = 1
                #if (total_signal) < cut*Ped.GetBinError(max_all_chan + 1)*R.sqrt(Ped.GetBinEntries(max_all_chan + 1)):
                #    soft_evt[0] = 1

		eta[0] = -1
		if wholecluster and not(NoisyEvt) and not (Noisehit):
			R0 = R1[0]
			L0 = L1[0]
			#if R1[0] < 0:  R0 = 0
			#if L1[0] < 0:  L0 = 0
			if (R0 + L0) == 0:
				print "zero alert ",max_reg_chan,reg_event[max_reg_chan],Ped.GetBinError(max_all_chan + 1),Ped.GetBinEntries(max_all_chan + 1),CM,R1[0],L1[0]
			if soft_evt[0]==0: 
				eta[0] = R0/(R0+L0)
				EtaHist.Fill(eta[0])
				toteta += 1
				if eta[0] > 0.2 and eta[0] < 0.8: mideta += 1
			#print eta[0], R0, L0, R1, L1
                	RTree.Fill()

                if (reg_event[max_reg_chan]-CM) < cut*Ped.GetBinError(max_all_chan + 1)*R.sqrt(Ped.GetBinEntries(max_all_chan + 1)):
                    NsoftSignal+=1
                    event_data = []
                    continue
                #if (total_signal) < cut*Ped.GetBinError(max_all_chan + 1)*R.sqrt(Ped.GetBinEntries(max_all_chan + 1)):
                #    NsoftSignal+=1
                #    event_data = []
                #    continue
		if NoisyEvt or Noisehit:
                    event_data = []
                    continue
                
		NgoodEvts+=1
                SignalHist1.Fill(seed_signal)
                SignalHist2.Fill(total_signal)
                SignalHist3.Fill(total_signal)

                
                event_data = []

    file.close()

    print 'START TIME: ',tmstamp
    print 'BAD EVENTS:',NbadChans
    print 'SOFT EVENTS:',NsoftSignal
    print 'NOISY EVENTS:',NnoisyEvts
    print 'NOISE HITS:',Nnoisehits
    print 'GOOD EVENTS:',NgoodEvts
    print 'ETA PCT:',float(mideta)/toteta
    print 'Hits ', hit1, hit2, hit3
    NoisyEvts[0] = NnoisyEvts
    SoftEvts[0] = NsoftSignal
    NoiseHits[0] = Nnoisehits
    EtaPct[0] = float(mideta)/toteta

    c1 = R.TCanvas('c1', 'Run ' + str(RunNum) + ' Summary', 200, 10, 800, 1000 )
    c1.Divide(2,2)
    c1.cd(1)
    SignalHist1.Draw()
    c1.cd(2)
    SignalHist2.Draw()
    c1.cd(3)
    Hit_Data.Draw()
    c1.cd(4)
    EtaHist.Draw()
    c1.SaveAs(RFile_name[:-5] + ".pdf")

    if RFile_name != '':
        #RFile = R.TFile(RFile_name,'UPDATE')
	c1.Write("",R.TObject.kOverwrite)
        StartTime[0] = float(tmstamp)/(60*60*24) #Get time in days since Jan 1, 1904 + 40500 days
        StartTime.Write("StartTime",R.TObject.kOverwrite)
	StartTemp.Write("StartTemp",R.TObject.kOverwrite)
	NoisyEvts.Write("NoisyEvents",R.TObject.kOverwrite)
	SoftEvts.Write("SoftEvents",R.TObject.kOverwrite)
	NoiseHits.Write("NoiseHits",R.TObject.kOverwrite)
	EtaPct.Write("EtaPct",R.TObject.kOverwrite)
	CMs.Write("",R.TObject.kOverwrite)
	Sig_Data.Write("",R.TObject.kOverwrite)
        SignalHist1.Write("",R.TObject.kOverwrite)
        SignalHist2.Write("",R.TObject.kOverwrite)
        SignalHist3.Write("",R.TObject.kOverwrite)
	EtaHist.Write("",R.TObject.kOverwrite)
	HitProf.Write("",R.TObject.kOverwrite)
        #RTree = RTree.Write("",R.TObject.kOverwrite)
        RFile.Close()

    #RTree.Write("",R.TObject.kOverwrite)
    RhdFile.Write("",R.TObject.kOverwrite)
    RhdFile.Close()

def get_signal3(file_name, region, Ped, title, RFile_name, bad_chans, RunNum, scale = 1, T_Array=0, stripstart=0, stripend=31, cut=0, extra = None):

    print "strips ", stripstart, stripend
    if extra == None: extra = 'R'+str(13-(region))
    file = open(file_name, 'r')    

    runno = array('i', [0])
    eventno = array('i', [0])
    hit_strip = array('i', 3*[0])
    clust_charge = array ('f', 3*[0.])
    strip_charge = array ('f', 3*[0.])
    #SR1_charge = array ('f', [0.])
    #SR2_charge = array ('f', [0.])
    #SL1_charge = array ('f', [0.])
    #SL2_charge = array ('f', [0.])
    R1 = array ('f', 3*[0.])
    R2 = array ('f', 3*[0.])
    L1 = array ('f', 3*[0.])
    L2 = array ('f', 3*[0.])
    eta = array ('f', 3*[0.])
    CM_noise = array ('f', 3*[0.])

    sig_noise = array ('f', 3*[0.])
    soft_evt = array ('i', 3*[0])
    T_Chuck = array ('f', [0.])


    RhdFile_name = RFile_name[:-5] + "_hd.root"
    print RhdFile_name
    RhdFile = R.TFile(RhdFile_name,'RECREATE')
    
    RTree = R.TTree('hits', 'Hit Data')
    RTree.Branch('runno',runno,'runno/I')
    RTree.Branch('eventno',eventno,'eventno/I')
    RTree.Branch('hit_strip',hit_strip,'hit_strip[3]/I')
    RTree.Branch('clust_charge',clust_charge,'clust_charge[3]/F')
    RTree.Branch('strip_charge',strip_charge,'strip_charge[3]/F')
    #RTree.Branch('SR1_charge',SR1_charge,'SR1_charge/F')
    #RTree.Branch('SR2_charge',SR2_charge,'SR2_charge/F')
    #RTree.Branch('SL1_charge',SL1_charge,'SL1_charge/F')
    #RTree.Branch('SL2_charge',SL2_charge,'SL2_charge/F')
    RTree.Branch('R1',R1,'R1[3]/F')
    RTree.Branch('R2',R2,'R2[3]/F')
    RTree.Branch('L1',L1,'L1[3]/F')
    RTree.Branch('L2',L2,'L2[3]/F')
    RTree.Branch('eta',eta,'eta[3]/F')
    RTree.Branch('CM_noise',CM_noise,'CM_noise[3]/F')
    RTree.Branch('sig_noise',sig_noise,'sig_noise[3]/F')
    RTree.Branch('soft_evt',soft_evt,'soft_evt[3]/I')
    RTree.Branch('T_Chuck',T_Chuck,'T_Chuck/F')

    if RFile_name != '':
        RFile = R.TFile(RFile_name,'UPDATE')

    CMs = R.TH1D('CMs '+extra,'CMs '+extra, 20, -5*scale, 5*scale)
    CMs.Sumw2()
    CMs.SetOption('hist')
    
    Sig_Data = R.TProfile(extra + ' Data',extra + ' Data',32, 0, 32)
    Sig_Data.Sumw2()
    Sig_Data.SetOption('colz')
    Sig_Data0 = R.TProfile(extra + '0 Data',extra + ' Data',32, 0, 32)
    Sig_Data0.Sumw2()
    Sig_Data0.SetOption('colz')
    Sig_Data1 = R.TProfile(extra + '1 Data',extra + ' Data',32, 0, 32)
    Sig_Data1.Sumw2()
    Sig_Data1.SetOption('colz')
    Sig_Data2 = R.TProfile(extra + '2 Data',extra + ' Data',32, 0, 32)
    Sig_Data2.Sumw2()
    Sig_Data2.SetOption('colz')
    Hit_Data = R.TH1D("HitStrip", "Hit Strip", 32, 0, 32)
    Hit_Data.Sumw2()
    Hit_Data.SetOption('hist')
    Hit_Data0 = R.TH1D("HitStrip0", "Hit Strip 0", 32, 0, 32)
    Hit_Data0.Sumw2()
    Hit_Data0.SetOption('hist')
    Hit_Data1 = R.TH1D("HitStrip1", "Hit Strip 1", 32, 0, 32)
    Hit_Data1.Sumw2()
    Hit_Data1.SetOption('hist')
    Hit_Data2 = R.TH1D("HitStrip2", "Hit Strip 2", 32, 0, 32)
    Hit_Data2.Sumw2()
    Hit_Data2.SetOption('hist')

    h_name_fine_bin = extra + ' Signal_' + '1000' + 'Bins'
    h_name_fine_bin_clust = extra + ' Signal_' + '1000' + 'Bins_clust'
    h_name_coarse_bin_clust = extra + ' Signal_' + '100' + 'Bins_clust'
    SignalHist1 = R.TH1D(h_name_fine_bin, h_name_fine_bin, 1000, 0, 100*scale)
    SignalHist1.Sumw2()
    SignalHist1.SetOption('hist')
    SignalHist2 = R.TH1D(h_name_fine_bin_clust, h_name_fine_bin_clust, 1000, 0, 100*scale)
    SignalHist2.Sumw2()
    SignalHist2.SetOption('hist')
    SignalHist3 = R.TH1D(h_name_coarse_bin_clust, h_name_coarse_bin_clust, 100, 0, 100*scale)
    SignalHist3.Sumw2()
    SignalHist3.SetOption('hist')
    SignalHist01 = R.TH1D(h_name_fine_bin+"0", h_name_fine_bin, 1000, 0, 100*scale)
    SignalHist01.Sumw2()
    SignalHist01.SetOption('hist')
    SignalHist02 = R.TH1D(h_name_fine_bin_clust+"0", h_name_fine_bin_clust, 1000, 0, 100*scale)
    SignalHist02.Sumw2()
    SignalHist02.SetOption('hist')
    SignalHist03 = R.TH1D(h_name_coarse_bin_clust+"0", h_name_coarse_bin_clust, 100, 0, 100*scale)
    SignalHist03.Sumw2()
    SignalHist03.SetOption('hist')
    SignalHist11 = R.TH1D(h_name_fine_bin+"1", h_name_fine_bin, 1000, 0, 100*scale)
    SignalHist11.Sumw2()
    SignalHist11.SetOption('hist')
    SignalHist12 = R.TH1D(h_name_fine_bin_clust+"1", h_name_fine_bin_clust, 1000, 0, 100*scale)
    SignalHist12.Sumw2()
    SignalHist12.SetOption('hist')
    SignalHist13 = R.TH1D(h_name_coarse_bin_clust+"1", h_name_coarse_bin_clust, 100, 0, 100*scale)
    SignalHist13.Sumw2()
    SignalHist13.SetOption('hist')
    SignalHist21 = R.TH1D(h_name_fine_bin+"2", h_name_fine_bin, 1000, 0, 100*scale)
    SignalHist21.Sumw2()
    SignalHist21.SetOption('hist')
    SignalHist22 = R.TH1D(h_name_fine_bin_clust+"2", h_name_fine_bin_clust, 1000, 0, 100*scale)
    SignalHist22.Sumw2()
    SignalHist22.SetOption('hist')
    SignalHist23 = R.TH1D(h_name_coarse_bin_clust+"2", h_name_coarse_bin_clust, 100, 0, 100*scale)
    SignalHist23.Sumw2()
    SignalHist23.SetOption('hist')
    SignalHist75ns = R.TH1D(h_name_fine_bin_clust+"75", h_name_fine_bin_clust, 1000, 0, 100*scale)
    SignalHist75ns.Sumw2()
    SignalHist75ns.SetOption('hist')
    EtaHist = R.TH1D("Eta","Eta", 120, -0.1, 1.1)
    EtaHist.Sumw2()
    EtaHist.SetOption('hist')
    EtaHist0 = R.TH1D("Eta0","Eta", 120, -0.1, 1.1)
    EtaHist0.Sumw2()
    EtaHist0.SetOption('hist')
    EtaHist1 = R.TH1D("Eta1","Eta", 120, -0.1, 1.1)
    EtaHist1.Sumw2()
    EtaHist1.SetOption('hist')
    EtaHist2 = R.TH1D("Eta2","Eta", 120, -0.1, 1.1)
    EtaHist2.Sumw2()
    EtaHist2.SetOption('hist')
    HitProf = R.TProfile("HitProf", "Hit Profile", 7, 0, 7)


    #Creates TObject to store time
    StartTime = R.TVectorF(1)
    StartTemp = R.TVectorF(1)
    NoisyEvts = R.TVectorF(3)
    SoftEvts = R.TVectorF(3)
    NoiseHits = R.TVectorF(3)
    EtaPct = R.TVectorF(3)
   
    runno[0] = RunNum
    event_data = []
    event_data0 = []
    event_data1 = []
    event_data2 = []
    StartTemp[0] = -99.0
    event = 0
    NbadChans = 0
    Nnoisehits = [0,0,0]
    NsoftSignal = [0,0,0]
    NnoisyEvts = [0,0,0]
    NgoodEvts = [0,0,0]
    Tindex = 0
    tmstamp = 0
    mideta = [0,0,0]
    toteta = [0,0,0]
    hit1 = hit2 = hit3 = 0

    print bad_chans
    for line in file:
        #Read out time from file
        if line[0:4] == 'Date':
            rdate = line.split(' ')[1].split('.')
            rtime = line.split(' ')[3].split(':')
            runtime = datetime(2000+int(rdate[2]),int(rdate[1]),int(rdate[0]),int(rtime[0]),int(rtime[1]),int(rtime[2])) - datetime(1904,1,1,0,0,0,0)
            lvtime = 24*60*60*float(runtime.days) + float(runtime.seconds/86400.00000)
            tmstamp = 24*60*60*runtime.days + runtime.seconds
            print rdate, rtime, runtime, runtime.days, runtime.seconds, tmstamp

        if line.count(',') > 3:
            event += 1
	    if event % 4 == 1:
	    	evttime = float(line.split('\t')[0])
		if evttime > tmstamp: tmstamp = evttime
		tca = get_temp (T_Array, tmstamp, Tindex)
		T_Chuck[0] = tca[0]
		Tindex = tca[1]
		if StartTemp[0] < 90: StartTemp[0] = T_Chuck[0]

            if event % 4000 == 0: print event/4
            
            full_event = [float(x) for x in line.replace('\r\t','').split('\t')[-1].split(',')]
            if scale != 1: event_data += [x*192000.0/full_event[-1] for x in full_event[12:-1]]
            else: 
		event_data0+=(full_event[12:140])
		event_data1+=(full_event[152:280])
		event_data2+=(full_event[292:420])
		event_data = [event_data0, event_data1, event_data2]
		#event_data += full_event[12:-1]
            
            if event % 4 == 0:
		eventno[0] = event/4
                #subtracted_event = [event_data[i] - Ped.GetBinContent(i+1) for i in range(512)]
                subtracted_event = [[event_data[0][j] - Ped.GetBinContent(j+1) for j in range(512)],[event_data[1][k] - Ped.GetBinContent(k+1) for k in range(512)],[event_data[2][l] - Ped.GetBinContent(l+1) for l in range(512)]]
                #apv_event = subtracted_event[(region+1)/4*128:(1+(region+1)/4)*128]
                #reg_event = subtracted_event[32*(region+1):32*(region+2)]
                apv_event = [subtracted_event[0][(region+1)/4*128:(1+(region+1)/4)*128],subtracted_event[1][(region+1)/4*128:(1+(region+1)/4)*128],subtracted_event[2][(region+1)/4*128:(1+(region+1)/4)*128]]
                reg_event = [subtracted_event[0][32*(region+1):32*(region+2)],subtracted_event[1][32*(region+1):32*(region+2)],subtracted_event[2][32*(region+1):32*(region+2)]]
		tot_event = [reg_event[0][i] + reg_event[1][i] + reg_event[2][i] for i in range(32)]                
                for chan in range(len(reg_event[0])):
                    #Sig_Data.Fill(chan, reg_event[0][chan])
                    #Sig_Data.Fill(chan, reg_event[1][chan])
                    #Sig_Data.Fill(chan, reg_event[2][chan])
                    Sig_Data.Fill(chan, tot_event[chan])
                    Sig_Data0.Fill(chan, reg_event[0][chan])
                    Sig_Data1.Fill(chan, reg_event[1][chan])
                    Sig_Data2.Fill(chan, reg_event[2][chan])

                #print max(subtracted_event), subtracted_event.index(max(subtracted_event))/32 - 1, max(reg_event), reg_event.index(max(reg_event))
                #raw_input('')
                
                #eventSN = []
                #for i in range(512):
                #    if Ped.GetBinError(i+1) == 0: eventSN.append(0)
                #    else: 
		#	eventSN.append( subtracted_event[0][i]/float(Ped.GetBinError(i+1)*R.sqrt(Ped.GetBinEntries(i+1))) )
		#	eventSN.append( subtracted_event[1][i]/float(Ped.GetBinError(i+1)*R.sqrt(Ped.GetBinEntries(i+1))) )
		#	eventSN.append( subtracted_event[2][i]/float(Ped.GetBinError(i+1)*R.sqrt(Ped.GetBinEntries(i+1))) )
            
            
                apv = (region+1)/4
                #apvSN = [eventSN[0][(region+1)/4*128:(1+(region+1)/4)*128],eventSN[1][(region+1)/4*128:(1+(region+1)/4)*128],eventSN[2][(region+1)/4*128:(1+(region+1)/4)*128]]
                #regSN = [eventSN[0][32*(region+1):32*(region+2)],eventSN[1][32*(region+1):32*(region+2)],eventSN[2][32*(region+1):32*(region+2)]]

		#for i in xrange(len(regSN)):
		#	if regSN[i] > 2.75: hit3 +=1
		#	if regSN[i] > 2.5: hit2 += 1
		#	if regSN[i] > 2.25: hit1 += 1
                
                chan_nums = [i for i in range(32)]
                
                good_regevt = [[reg_event[0][i] for i in range(32) if i not in bad_chans],[reg_event[1][i] for i in range(32) if i not in bad_chans],[reg_event[2][i] for i in range(32) if i not in bad_chans]]
                good_totevt = [tot_event[i] for i in range(32) if i not in bad_chans]
                #good_regSN = [[regSN[0][i] for i in range(32) if i not in bad_chans],[regSN[1][i] for i in range(32) if i not in bad_chans],[regSN[2][i] for i in range(32) if i not in bad_chans]]
                goodchan_nums = [chan_nums[i] for i in range(32) if i not in bad_chans]
                
                #Takes max signal to noise
                #good_max_reg_chan = good_regSN.index(max(good_regSN))
                good_max_reg_chan = [good_regevt[0].index(max(good_regevt[0])),good_regevt[1].index(max(good_regevt[1])),good_regevt[2].index(max(good_regevt[2]))]
                good_max_tot_chan = good_totevt.index(max(good_totevt))
                max_reg_chan = [goodchan_nums[good_max_reg_chan[0]],goodchan_nums[good_max_reg_chan[1]],goodchan_nums[good_max_reg_chan[2]]]
                max_tot_chan = goodchan_nums[good_max_tot_chan]
		                
                if max_reg_chan in bad_chans: print max_reg_chan
                max_apv_chan = [((region+1)%4)*32 + max_reg_chan[0],((region+1)%4)*32 + max_reg_chan[1],((region+1)%4)*32 + max_reg_chan[2]]
                max_all_chan = [(region+1)*32 + max_reg_chan[0],(region+1)*32 + max_reg_chan[1],(region+1)*32 + max_reg_chan[2]]
                for i in xrange(3): hit_strip[i] = max_reg_chan[i]
		Noisehit = [False,False,False]
                if max_reg_chan[0] < stripstart or max_reg_chan[0] > stripend:
			Noisehit[0] = True
			Nnoisehits[1] += 1
		else:
			Hit_Data.Fill(max_reg_chan[0])
			Hit_Data0.Fill(max_reg_chan[0])		
                if max_reg_chan[1] < stripstart or max_reg_chan[1] > stripend:
			Noisehit[1] = True
			Nnoisehits[1] += 1
		else:
			Hit_Data.Fill(max_reg_chan[1])
			Hit_Data1.Fill(max_reg_chan[1])		
                if max_reg_chan[2] < stripstart or max_reg_chan[2] > stripend:
			Noisehit[2] = True
			Nnoisehits[2] += 1
		else:
			Hit_Data.Fill(max_reg_chan[2])
			Hit_Data2.Fill(max_reg_chan[2])		

                #max_reg_chan = reg_event.index(max(reg_event))
                #max_apv_chan = ((region+1)%4)*32 + max_reg_chan
                #max_all_chan = (region+1)*32 + max_reg_chan
                
                #CM = sum(apv_event) - apv_event[max_apv_chan]
                #count = 127.0

		#Loop over APV events and subtract off neighbors of the hit strip and bad/noisy channels
		#for i in xrange(128):
                #	if abs(max_apv_chan - 1) == 1:
                #    		CM -= apv_event[i]
                #    		count -= 1
                #	if ((128*apv) + i) in bad_chans:
		#		#print "removing bad_chan", i, apv_event[i]
                #    		CM -= apv_event[i]
                #    		count -= 1

                CM = [sum(reg_event[0]) - reg_event[0][max_reg_chan[0]],sum(reg_event[1]) - reg_event[1][max_reg_chan[1]],sum(reg_event[2]) - reg_event[2][max_reg_chan[2]]]
                count = [31.0, 31.0, 31.0]

		#Loop over APV events and subtract off neighbors of the hit strip and bad/noisy channels
		for j in xrange(3):
                   if ((max_reg_chan[j] - 1) >=0) and ((max_reg_chan[j] - 1) not in bad_chans):
                    	CM[j] -= reg_event[j][max_reg_chan[j]-1]
                    	count[j] -= 1
                   if ((max_reg_chan[j] + 1) <32) and ((max_reg_chan[j] + 1) not in bad_chans):
                    	CM[j] -= reg_event[j][max_reg_chan[j]+1]
                    	count[j] -= 1
		   for i in xrange(32):
                	if i in bad_chans:
				#print "removing bad_chan", i, apv_event[i]
                    		CM[j] -= reg_event[j][i]
                    		count[j] -= 1
                
                   CM[j] /= count[j]
                   CMs.Fill(CM[j])
		   NoisyEvt = [False,False,False]
		   SoftEvt = [False,False,False]
		   if abs(CM[j]) > 5:	
			NoisyEvt[j] = True
                	NnoisyEvts[j]+=1

                   if max_reg_chan in bad_chans:
                    	event_data = []
                    	NbadChans+=1
                    	continue

                for i in xrange(3): CM_noise[i] = CM[i]
            
                #if( apv_event[max_apv_chan] > 10): print apv_event[max_apv_chan], CM
                    
                #Fill unclustered histogram and tree brances
		totCM = (CM[0]+CM[1]+CM[2])/3
		#print tot_event, max_tot_chan
		totseed_signal = tot_event[max_tot_chan] - totCM
		totclust_signal = totseed_signal
                seed_signal = [apv_event[0][max_apv_chan[0]] - CM[0], apv_event[1][max_apv_chan[1]] - CM[1], apv_event[2][max_apv_chan[2]] - CM[2]]
		total_signal = [seed_signal[0],seed_signal[1],seed_signal[2]]
                for i in xrange(3): strip_charge[i] = seed_signal[i]
		#print event/4, event_data[0][0],apv_event[0][0],seed_signal, max_apv_chan, CM

		#If hit is not on edges record entire 4 strip cluster
		#Possibly a bias if significant number of apv_evt[chan-1] = apv_evt[chan+1]
		wholecluster = [False,False,False]
		#print "max_reg_chan", max_reg_chan
		for i in xrange(3):
		  if (max_reg_chan[i] > 0) and (max_reg_chan[i] < 31): 
		   if apv_event[i][max_apv_chan[i]+1] > apv_event[i][max_apv_chan[i]-1]:
			if ((max_reg_chan[i] + 2) < 32) and ((max_reg_chan[i] - 1) > -1):
				L1[i] = apv_event[i][max_apv_chan[i]] - CM[i]
				R1[i] = apv_event[i][max_apv_chan[i]+1] - CM[i]
				L2[i] = apv_event[i][max_apv_chan[i]-1] - CM[i]
				R2[i] = apv_event[i][max_apv_chan[i]+2] - CM[i]
				wholecluster[i] = True
		   else:
			if ((max_reg_chan[i] + 1) < 32) and ((max_reg_chan[i] - 2) > -1):
				L1[i] = apv_event[i][max_apv_chan[i]-1] - CM[i]
				R1[i] = apv_event[i][max_apv_chan[i]] - CM[i]
				L2[i] = apv_event[i][max_apv_chan[i]-2] - CM[i]
				R2[i] = apv_event[i][max_apv_chan[i]+1] - CM[i]
				wholecluster[i] = True
		   if apv_event[i][max_apv_chan[i]+1] == apv_event[i][max_apv_chan[i]-1]: print "Left & Right neighbors equal charge!"


                #Do clustering and fill histograms. Change from 2 -> 1 times the noise to get counted in cluster
		#Now just add neighbors without doing a cut
		HitProf.Fill(3,apv_event[0][max_apv_chan[0]]-CM[0])
		HitProf.Fill(3,apv_event[1][max_apv_chan[1]]-CM[1])
		HitProf.Fill(3,apv_event[2][max_apv_chan[2]]-CM[2])
		if max_tot_chan < 31: totclust_signal += tot_event[max_tot_chan+1] - totCM
		if max_tot_chan > 0: totclust_signal += tot_event[max_tot_chan-1] - totCM
		for i in xrange(3):
                  if (max_reg_chan[i] + 1) < 32:
                    total_signal[i] += apv_event[i][max_apv_chan[i]+1] - CM[i]
		    HitProf.Fill(4,apv_event[i][max_apv_chan[i]+1]-CM[i])
                    #if (apv_event[max_apv_chan+1]-CM) > 1*Ped.GetBinError(max_all_chan + 1 + 1)*R.sqrt(Ped.GetBinEntries(max_all_chan + 1 + 1)): total_signal += apv_event[max_apv_chan+1] - CM
                    #SR1_charge[0] = apv_event[max_apv_chan+1] - CM
                    #if (max_reg_chan + 2) < 32:  SR2_charge[0] = apv_event[max_apv_chan+2] - CM
                  if (max_reg_chan[i] - 1) > -1:
                    total_signal[i] += apv_event[i][max_apv_chan[i]-1] - CM[i]
		    HitProf.Fill(2,apv_event[i][max_apv_chan[i]-1]-CM[i])
                    #if (apv_event[max_apv_chan-1]-CM) > 1*Ped.GetBinError(max_all_chan - 1 + 1)*R.sqrt(Ped.GetBinEntries(max_all_chan - 1 + 1)): total_signal += apv_event[max_apv_chan-1] - CM
                    #SL1_charge[0] = apv_event[max_apv_chan-1] - CM
                    #if (max_reg_chan - 2) > -1:  SL2_charge[0] = apv_event[max_apv_chan-2] - CM
                #if (max_reg_chan - 2) > -1:  HitProf.Fill(1, apv_event[max_apv_chan-2]-CM)
                #if (max_reg_chan + 2) < 32:  HitProf.Fill(5, apv_event[max_apv_chan+2]-CM)
                #if (max_reg_chan - 3) > -1:  HitProf.Fill(1, apv_event[max_apv_chan-3]-CM)
                #if (max_reg_chan + 3) < 32:  HitProf.Fill(5, apv_event[max_apv_chan+3]-CM)
                     


                for i in xrange(3): clust_charge[i] = total_signal[i]

                #Mark soft events (less than 3x noise) in tree (was previously 5x noise)
                soft_evt[0] = 0
		#if Ped.GetBinError(max_all_chan + 1)*R.sqrt(Ped.GetBinEntries(max_all_chan + 1)) == 0:
		#	print Ped.GetBinError(max_all_chan + 1), Ped.GetBinEntries(max_all_chan + 1), max_all_chan
		#	sig_noise[0] = 0
                #else: sig_noise[0] = float(reg_event[max_reg_chan])/(Ped.GetBinError(max_all_chan + 1)*R.sqrt(Ped.GetBinEntries(max_all_chan + 1)))
                #sig_noise[0] = float(reg_event[max_reg_chan])/(Ped.GetBinError(max_all_chan + 1)*R.sqrt(Ped.GetBinEntries(max_all_chan + 1)))
		for i in xrange(3):
                	if (reg_event[i][max_reg_chan[i]]-CM[i]) < cut*Ped.GetBinError(max_all_chan[i] + 1)*R.sqrt(Ped.GetBinEntries(max_all_chan[i] + 1)):
                    		soft_evt[i] = 1
                #if (total_signal) < cut*Ped.GetBinError(max_all_chan + 1)*R.sqrt(Ped.GetBinEntries(max_all_chan + 1)):
                #    soft_evt[0] = 1

		for i in xrange(3):
		   eta[i] = -1
		   if wholecluster[i] and not(NoisyEvt[i]) and not (Noisehit[i]):
			R0 = R1[i]
			L0 = L1[i]
			#if R1[0] < 0:  R0 = 0
			#if L1[0] < 0:  L0 = 0
			if (R0 + L0) == 0:
				print "zero alert ",max_reg_chan,reg_event[max_reg_chan],Ped.GetBinError(max_all_chan + 1),Ped.GetBinEntries(max_all_chan + 1),CM,R1[0],L1[0]
			if soft_evt[i]==0: 
				eta[i] = R0/(R0+L0)
				EtaHist.Fill(eta[i])
				if i == 0: EtaHist0.Fill(eta[i])
				if i == 1: EtaHist1.Fill(eta[i])
				if i == 2: EtaHist2.Fill(eta[i])
				toteta[i] += 1
				if eta[i] > 0.2 and eta[i] < 0.8: mideta[i] += 1
			#else: print "soft event"
			#print eta[0], R0, L0, R1, L1
                	

		BadEvent = False
		for i in xrange(3):
                  if (reg_event[i][max_reg_chan[i]]-CM[i]) < cut*Ped.GetBinError(max_all_chan[i] + 1)*R.sqrt(Ped.GetBinEntries(max_all_chan[i] + 1)):
                    NsoftSignal[i]+=1
                    event_data0 = []
                    event_data1 = []
                    event_data2 = []
                    #event_data = []
                    BadEvent = True
                  if (total_signal[i]) < cut*Ped.GetBinError(max_all_chan[i] + 1)*R.sqrt(Ped.GetBinEntries(max_all_chan[i] + 1)): 
		    NsoftSignal[i]+=1
		    SoftEvt[i] = True
		  if NoisyEvt[i] or Noisehit[i] or SoftEvt[i] or not(wholecluster[i]):
                    event_data0 = []
                    event_data1 = []
                    event_data2 = []
                    #event_data = []
                    BadEvent = True
		if BadEvent: continue
		for i in xrange(3):
			if abs(eta[i]-0.5) > 1: 
				print event/4, eta[0], R1[0], L1[0], hit_strip[0], CM[0], eta[1], R1[1], L1[1], hit_strip[1], CM[1], eta[2], R1[2], L1[2], hit_strip[2], CM[2]
				#print event_data1
				#print apv_event[1]
				print reg_event[0]
				print reg_event[1]
				print reg_event[2]
		RTree.Fill()
                
		for i in xrange(3):
			NgoodEvts[i]+=1
                	#SignalHist1.Fill(seed_signal[i])
                	#SignalHist2.Fill(total_signal[i])
                	#SignalHist3.Fill(total_signal[i])
		SignalHist1.Fill(totseed_signal)
		SignalHist2.Fill(totclust_signal)
		SignalHist3.Fill(totclust_signal)
                SignalHist01.Fill(seed_signal[0])
                SignalHist02.Fill(total_signal[0])
                SignalHist03.Fill(total_signal[0])
                SignalHist11.Fill(seed_signal[1])
                SignalHist12.Fill(total_signal[1])
                SignalHist13.Fill(total_signal[1])
                SignalHist21.Fill(seed_signal[2])
                SignalHist22.Fill(total_signal[2])
                SignalHist23.Fill(total_signal[2])
                SignalHist75ns.Fill(total_signal[0]+total_signal[1]+total_signal[2])

                
                event_data0 = []
                event_data1 = []
                event_data2 = []

    file.close()

    print 'START TIME: ',tmstamp
    print 'BAD EVENTS:',NbadChans
    print 'SOFT EVENTS:',NsoftSignal
    print 'NOISY EVENTS:',NnoisyEvts
    print 'NOISE HITS:',Nnoisehits
    print 'GOOD EVENTS:',NgoodEvts
    print 'ETA PCT:',float(mideta[0])/toteta[0],float(mideta[1])/toteta[1],float(mideta[2])/toteta[2] 
    print 'Hits ', hit1, hit2, hit3
    NoisyEvts[0] = NnoisyEvts[0]
    NoisyEvts[1] = NnoisyEvts[1]
    SoftEvts[0] = NsoftSignal[0]
    NoiseHits[0] = Nnoisehits[0]
    #EtaPct[0] = float(mideta)/toteta

    c1 = R.TCanvas('c1', 'Run ' + str(RunNum) + ' Summary', 200, 10, 800, 1000 )
    c1.Divide(2,2)
    c1.cd(1)
    SignalHist01.Draw()
    c1.cd(2)
    SignalHist02.Draw()
    c1.cd(3)
    Hit_Data0.Draw()
    c1.cd(4)
    EtaHist0.Draw()
    c1.SaveAs(RFile_name[:-5] + ".pdf")

    if RFile_name != '':
        #RFile = R.TFile(RFile_name,'UPDATE')
	c1.Write("",R.TObject.kOverwrite)
        StartTime[0] = float(tmstamp)/(60*60*24) #Get time in days since Jan 1, 1904 + 40500 days
        StartTime.Write("StartTime",R.TObject.kOverwrite)
	StartTemp.Write("StartTemp",R.TObject.kOverwrite)
	NoisyEvts.Write("NoisyEvents",R.TObject.kOverwrite)
	SoftEvts.Write("SoftEvents",R.TObject.kOverwrite)
	NoiseHits.Write("NoiseHits",R.TObject.kOverwrite)
	EtaPct.Write("EtaPct",R.TObject.kOverwrite)
	CMs.Write("",R.TObject.kOverwrite)
	Sig_Data.Write("",R.TObject.kOverwrite)
	Sig_Data0.Write("",R.TObject.kOverwrite)
	Sig_Data1.Write("",R.TObject.kOverwrite)
	Sig_Data2.Write("",R.TObject.kOverwrite)
	Hit_Data.Write("",R.TObject.kOverwrite)
	Hit_Data0.Write("",R.TObject.kOverwrite)
	Hit_Data1.Write("",R.TObject.kOverwrite)
	Hit_Data2.Write("",R.TObject.kOverwrite)
        SignalHist1.Write("",R.TObject.kOverwrite)
        SignalHist2.Write("",R.TObject.kOverwrite)
        SignalHist3.Write("",R.TObject.kOverwrite)
        SignalHist01.Write("",R.TObject.kOverwrite)
        SignalHist02.Write("",R.TObject.kOverwrite)
        SignalHist03.Write("",R.TObject.kOverwrite)
        SignalHist11.Write("",R.TObject.kOverwrite)
        SignalHist12.Write("",R.TObject.kOverwrite)
        SignalHist13.Write("",R.TObject.kOverwrite)
        SignalHist21.Write("",R.TObject.kOverwrite)
        SignalHist22.Write("",R.TObject.kOverwrite)
        SignalHist23.Write("",R.TObject.kOverwrite)
        SignalHist75ns.Write("",R.TObject.kOverwrite)
	EtaHist.Write("",R.TObject.kOverwrite)
	EtaHist0.Write("",R.TObject.kOverwrite)
	EtaHist1.Write("",R.TObject.kOverwrite)
	EtaHist2.Write("",R.TObject.kOverwrite)
	HitProf.Write("",R.TObject.kOverwrite)
        #RTree = RTree.Write("",R.TObject.kOverwrite)
        RFile.Close()

    #RTree.Write("",R.TObject.kOverwrite)
    RhdFile.Write("",R.TObject.kOverwrite)
    RhdFile.Close()

def doSimpleLandau(RFile_name, region, start=10, scale=1, extra=None): #start=85 was default in Methods, but in stream.py start=10 wass specified

	Landau_Chi2 = R.TVectorF(1)
	i = start

	if extra == None: extra = 'R'+str(13-(region))
	h_name_coarse_bin_clust = extra + ' Signal_' + '100' + 'Bins_clust'	
        hist_name = h_name_coarse_bin_clust

       	R.gROOT.ProcessLine('LandauFit("' + RFile_name + '","' + hist_name + '","' + extra + '",'+str(scale)+','+str(i)+')')
       	RFile = R.TFile(RFile_name,'UPDATE')
       	chi2 = RFile.Get(hist_name).GetFunction(extra+'_Func').GetChisquare()
       	print chi2, RFile.Get(hist_name).GetFunction(extra+'_Func').GetMaximumX(), i
	Landau_Chi2[0] = chi2
	Landau_Chi2.Write("Chi2")
       	RFile.Close()

def doSimpleLandau3(RFile_name, region, start=10, scale=1, extra=None): #start=85 was default in Methods, but in stream.py start=10 wass specified

	Landau_Chi2 = R.TVectorF(1)
	Landau_Chi20 = R.TVectorF(1)
	Landau_Chi21 = R.TVectorF(1)
	Landau_Chi22 = R.TVectorF(1)
	i = start

	if extra == None: extra = 'R'+str(13-(region))
	h_name_coarse_bin_clust = extra + ' Signal_' + '100' + 'Bins_clust'	
        hist_name = h_name_coarse_bin_clust
        hist_name0 = hist_name + "0"
        hist_name1 = hist_name + "1"
        hist_name2 = hist_name + "2"
	print hist_name0, hist_name1, hist_name2

       	R.gROOT.ProcessLine('LandauFit("' + RFile_name + '","' + hist_name + '","' + extra + '",'+str(scale)+','+str(i)+')')
       	R.gROOT.ProcessLine('LandauFit("' + RFile_name + '","' + hist_name0 + '","' + extra + '0",'+str(scale)+','+str(i)+')')
       	R.gROOT.ProcessLine('LandauFit("' + RFile_name + '","' + hist_name1 + '","' + extra + '1",'+str(scale)+','+str(i)+')')
       	R.gROOT.ProcessLine('LandauFit("' + RFile_name + '","' + hist_name2 + '","' + extra + '2",'+str(scale)+','+str(i)+')')
       	RFile = R.TFile(RFile_name,'UPDATE')
       	chi2 = RFile.Get(hist_name).GetFunction(extra+'_Func').GetChisquare()
       	print chi2, RFile.Get(hist_name).GetFunction(extra+'_Func').GetMaximumX(), i
	Landau_Chi2[0] = chi2 
       	chi2 = RFile.Get(hist_name).GetFunction(extra+'_Func').GetChisquare()
       	print chi2, RFile.Get(hist_name0).GetFunction(extra+'0_Func').GetMaximumX(), i
	Landau_Chi20[0] = chi2
       	chi2 = RFile.Get(hist_name).GetFunction(extra+'_Func').GetChisquare()
       	print chi2, RFile.Get(hist_name1).GetFunction(extra+'1_Func').GetMaximumX(), i
	Landau_Chi21[0] = chi2
       	chi2 = RFile.Get(hist_name).GetFunction(extra+'_Func').GetChisquare()
       	print chi2, RFile.Get(hist_name2).GetFunction(extra+'2_Func').GetMaximumX(), i
	Landau_Chi22[0] = chi2
	Landau_Chi2.Write("Chi2")
	Landau_Chi20.Write("Chi20")
	Landau_Chi21.Write("Chi21")
	Landau_Chi22.Write("Chi22")
       	RFile.Close()


def doLandau(RFile_name, region, start=10, scale=1, extra=None): #start=85 was default in Methods, but in stream.py start=10 wass specified

	i = start

	if extra == None: extra = 'R'+str(13-(region))
	h_name_coarse_bin_clust = extra + ' Signal_' + '100' + 'Bins_clust'	
        hist_name = h_name_coarse_bin_clust

       	R.gROOT.ProcessLine('LandauFit("' + RFile_name + '","' + hist_name + '","' + extra + '",'+str(scale)+','+str(i-1)+')')
       	RFile = R.TFile(RFile_name,'READ')
       	chi2_before = RFile.Get(hist_name).GetFunction(extra+'_Func').GetChisquare()
       	RFile.Close()

       	R.gROOT.ProcessLine('LandauFit("' + RFile_name + '","' + hist_name + '","' + extra + '",'+str(scale)+','+str(i+1)+')')
       	RFile = R.TFile(RFile_name,'READ')
       	chi2_after = RFile.Get(hist_name).GetFunction(extra+'_Func').GetChisquare()
       	RFile.Close()

       	R.gROOT.ProcessLine('LandauFit("' + RFile_name + '","' + hist_name + '","' + extra + '",'+str(scale)+','+str(i)+')')
       	RFile = R.TFile(RFile_name,'READ')
       	chi2 = RFile.Get(hist_name).GetFunction(extra+'_Func').GetChisquare()
       	RFile.Close()
       	print chi2_before, chi2, chi2_after

       	if (chi2 > chi2_before and chi2 < chi2_after) or (chi2 > chi2_before and chi2 > chi2_after and chi2_before < chi2_after):
       		while chi2 >= chi2_before or chi2 > chi2_after or chi2 > 500:
       			i -= 1.0
       			chi2_after = chi2
       			chi2 = chi2_before

       			R.gROOT.ProcessLine('LandauFit("' + RFile_name + '","' + hist_name + '","' + extra + '",'+str(scale)+','+str(i)+')')
       			RFile = R.TFile(RFile_name,'READ')
       			chi2_before = RFile.Get(hist_name).GetFunction(extra+'_Func').GetChisquare()
       			print chi2, RFile.Get(hist_name).GetFunction(extra+'_Func').GetMaximumX(), i
       			RFile.Close()
       		i += 1.0

       	elif (chi2 < chi2_before and chi2 > chi2_after) or (chi2 > chi2_before and chi2 > chi2_after and chi2_before > chi2_after):
       		while chi2 > chi2_before or chi2 >= chi2_after or chi2 > 500:
       			i += 1.0
       			chi2_before = chi2
       			chi2 = chi2_after
			
       			R.gROOT.ProcessLine('LandauFit("' + RFile_name + '","' + hist_name + '","' + extra + '",'+str(scale)+','+str(i)+')')
       			RFile = R.TFile(RFile_name,'READ')
       			chi2_after = RFile.Get(hist_name).GetFunction(extra+'_Func').GetChisquare()
       			print chi2, RFile.Get(hist_name).GetFunction(extra+'_Func').GetMaximumX(), i
       			RFile.Close()
       		i -= 1.0

       	R.gROOT.ProcessLine('LandauFit("' + RFile_name + '","' + hist_name + '","' + extra + '",'+str(scale)+','+str(i+1)+')')
       	RFile = R.TFile(RFile_name,'READ')
       	chi2_after = RFile.Get(hist_name).GetFunction(extra+'_Func').GetChisquare()
       	print chi2, RFile.Get(hist_name).GetFunction(extra+'_Func').GetMaximumX(), i
	RFile.Close()
	

def get_signalDoubleMetal_strip(file_name, chan_start, chan_end, Ped, inCMreg, bad_chans, NoiCM,  title, RFile_name, dd=0, scale = 1, extra = None, start = 10.0):

    print 'Get Signal...'
    if extra == None: extra = str(title)

    extra = str(extra)
    #find CMreg in the (start_chan,end_chan)region
    if chan_start!=inCMreg[0] or chan_end+1 != inCMreg[len(inCMreg)-1]: 
        CMreg = get_CMreg(inCMreg,chan_start,chan_end)
        print 'in'
        
    else: CMreg = list(inCMreg)

    #find bad channel in the (start_chan,end_chan)region
    Rbad_chans = get_bad_chan_in_region(bad_chans, chan_start, chan_end)
    Rbad_chan_plus = find_bad_chan2_plus(Rbad_chans)
    Rbad_in_reg = sort_bad_chan_into_reg(CMreg,Rbad_chans)
        
    data_file = open(file_name,'r')

    nchan = abs(chan_end-chan_start)+1
    #print chan_start,' ',chan_end,' ',nchan

    noise = [Ped.GetBinError(i+1)*R.sqrt(Ped.GetBinEntries(i+1)) for i in range(512)]
    #for i in range(chan_start,chan_end+1): NoiseDist.Fill(noise[i])

    HitStrip = R.TH1F('Hit Dist '+extra,'Hit Distribution',10,0,10)
    HitStrip.SetOption('hist')
    HitStrip.GetXaxis().SetTitle('# Hit strips')
    #HitStrip.GetYaxis().SetTitle('Entries')  

    #CM(Common mode noise) from signal data(in range chan_start,chan_end)   
    CMmed = R.TProfile('Data CMmed '+title,'Data CMmed '+title,nchan,chan_start,chan_end+1)
    CMmed.Sumw2()
    CMmed.SetOption('colz')
    CMmed.GetXaxis().SetTitle('APV Channel')
    CMmed.GetYaxis().SetTitle('CM [ADC count]')

    #CM distribution 
    CMDist = R.TH1F('DataCM Dist '+extra,'DataCM Distribution '+extra, 40, -5*scale, 5*scale)
    CMDist.Sumw2()
    CMDist.SetOption('hist')
    CMDist.GetXaxis().SetTitle('Common Mode Noise [ADC]')
    
    #total signal
    SignalHist = R.TH1D('Signal '+extra,extra + ' Signal',120, 0, 120*scale)
    SignalHist.Sumw2()
    SignalHist.SetOption('hist')
    SignalHist.GetXaxis().SetTitle('Signal [ADC Counts]')
    SignalHist.GetYaxis().SetTitle('#Events')
    
    # read only signal from max-signal strips with double layer (even strips)
    SignalDL = R.TH1D(extra + ' DL_Signal',extra+' DL_Signal',120,0,120*scale)
    SignalDL.Sumw2()
    SignalDL.SetOption('hist')
    SignalDL.GetXaxis().SetTitle('Signal [ADC Counts]')
    SignalDL.GetYaxis().SetTitle('#Events')

    # read only signal from max-signal strips with NO double layer (Reference) (odd strips)
    SignalREF = R.TH1D(extra +' NODL_Signal',extra+' NODL_Signal',120,0,120*scale)
    SignalREF.Sumw2()
    SignalREF.SetOption('hist')
    SignalREF.GetXaxis().SetTitle('Signal [ADC Counts]')
    SignalREF.GetYaxis().SetTitle('#Events')
    
    # Sig_Data = raw - ped -cm of each channel 
    #Sig_Data with Median cm
    Sig_Data2 = R.TProfile(extra + ' Data2',extra + ' Data2(with Median CM)',nchan, 0, nchan)
    Sig_Data2.Sumw2()
    Sig_Data2.SetOption('colz')
    Sig_Data2.GetXaxis().SetTitle(extra+' Channel')
    Sig_Data2.GetYaxis().SetTitle('Avg. signal [ADC count]')
    
    Sig_Data3 = R.TH2D(extra + ' Data3',extra + ' Data3',nchan, 0, nchan, 150, -75.5*scale, 74.5*scale)
    Sig_Data3.Sumw2()
    Sig_Data3.SetOption('colz')
    Sig_Data3.GetXaxis().SetTitle(extra+' Channel')
    Sig_Data3.GetYaxis().SetTitle('Signal[ADC count]')
    
    #signal from strips with no hit for calculating noise
    #with Median cm
    NoiSig2 = R.TProfile('Data NoiSig2' + title,'Data Noise Signal2 ' + title,nchan,0,nchan)
    NoiSig2.Sumw2() #Calculates TRUE average
    NoiSig2.SetOption('colz')
    NoiSig2.GetXaxis().SetTitle('APV Channel')
    NoiSig2.GetYaxis().SetTitle('Avg. signal [ADC count]')
    
    #CM subtracted noise from data
    #with Median cm
    NoiCMdat2 = R.TProfile('DataCMsub Noise2 '+title,'CM subtracted Noise '+title,nchan,0,nchan)
    NoiCMdat2.GetXaxis().SetTitle('APV Channel')
    NoiCMdat2.GetYaxis().SetTitle('CM subtracted Noise [ADC count]')
    
  #  NoiCMdatDist = R.TH1F('DataCMsub Noise Dist '+extra,'CM subtracted Noise distribution '+title,80,0,5)
  #  NoiCMdatDist.SetOption('hist')
  #  NoiCMdatDist.GetXaxis().SetTitle('Noise Distribution')
    
    NoiCMPrePed = R.TProfile('PrePedCMsub Noise_part '+title,'CM subtracted Noise '+title,nchan,0,nchan)
    NoiCMPrePed.GetXaxis().SetTitle('APV Channel')
    NoiCMPrePed.GetYaxis().SetTitle('CM subtracted Noise [ADC count]')

    #signal to noise ratio
    SN = R.TH1D(extra + ' SN',extra + ' Signal to Noise ratio',200, 0, 100)
    SN.Sumw2()
    SN.SetOption('hist')
    SN.GetXaxis().SetTitle('Signal to noise ratio')
    SN.GetYaxis().SetTitle('Entries')

    SNn = R.TH1D(extra + ' SN no double',extra + ' Signal to Noise ratio (No Double metal)',200, 0, 100)
    SNn.Sumw2()
    SNn.SetOption('hist')
    SNn.GetXaxis().SetTitle('Signal to noise ratio')
    SNn.GetYaxis().SetTitle('Entries')
    
    if dd:
        SNd = R.TH1D(extra + ' SN double',extra + ' Signal to Noise ratio (Double metal)',200, 0, 100)
        SNd.Sumw2()
        SNd.SetOption('hist')
        SNd.GetXaxis().SetTitle('Signal to noise ratio')
        SNd.GetYaxis().SetTitle('Entries')
    
    # signal for each strip
    stripSig = []
    stripSN = []
    
    for i in range(nchan):
        stripSig.append(R.TH1D('Sig_'+str(i+chan_start)+'_'+title,'Sig_'+str(i+chan_start)+'_'+title,120, 0, 120))
        stripSig[i].Sumw2()
        stripSig[i].SetOption('hist')
        stripSig[i].GetXaxis().SetTitle('Signal [ADC Count]')
        stripSig[i].GetYaxis().SetTitle('Entries')
        
        stripSN.append(R.TH1D('SN_'+str(i+chan_start)+'_'+title,'SN_'+str(i+chan_start)+'_'+title,200, 0, 100))
        stripSN[i].Sumw2()
        stripSN[i].SetOption('hist')
        stripSN[i].GetXaxis().SetTitle('S/N')
        stripSN[i].GetYaxis().SetTitle('Entries')
    
    HitEntries = R.TProfile(extra + ' HitEntries',extra + ' HitEntries',nchan, 0, nchan)
    HitEntries.SetOption('colz')
    HitEntries.GetXaxis().SetTitle(extra+' Channel')
    HitEntries.GetYaxis().SetTitle('Entries')
    
    Eta = R.TH1D('Eta6'+'_'+title,'Eta '+'_'+title,1000, -5.0, 5.0)
    Eta.Sumw2()
    Eta.SetOption('hist')
    Eta.GetXaxis().SetTitle('#eta')
    Eta.GetYaxis().SetTitle('Entries')
    
    event_data = [] #stores data from 512 channels of 1 event
    event = 0 #Counts the number of events ~ number of lines with data
    kk=-1
    skip_count = 0
    edge_count = 0
    for line in data_file:
        #Only looks at lines with data in them
        if line.count(',') > 3:
            event += 1 #increments the event count
            if event % 4000 == 0: print event/4 #Prints status
            #APV events
            full_event = [float(x) for x in line.replace('\r\t','').split('\t')[-1].split(',')]
            #scale and store all 4 APVs
            if scale != 1: event_data += [x*192000.0/full_event[-1] for x in full_event[12:-1]]
            else: event_data += full_event[12:-1]

            if event % 4 == 0:

                subtracted_event = [(event_data[i] - Ped.GetBinContent(i+1)) for i in range(len(event_data))]
                
                #max channel in the input region 
                #(1) not include bad chan and their neighbours for max selection
                for i in Rbad_chan_plus: subtracted_event[i] -= 100  
                max_chan = subtracted_event.index(max(subtracted_event[chan_start:chan_end+1]))
                
                #(2) not include edge
                if max_chan==chan_start or max_chan==chan_end: event_data=[]; edge_count +=1; continue
                
                #(3.1) (coarse screen) not include low signal < *Raw_noise
                if subtracted_event[max_chan] < 2*noise[max_chan]: event_data=[]; skip_count +=1; continue # print 'skip1';
                    
                for i in Rbad_chan_plus: subtracted_event[i] += 100 
                
                #find the region of max channel
                max_reg = 1
                if len(CMreg)!=2: max_reg = find_reg_of_chan(CMreg,max_chan); #print max_reg
                
                #####find CM (median CM)
                cm_med=[]
                temp_med=[]
                r=1  #region index
                for chan in range(chan_start,chan_end+2):
                
                    #add all channels in the region except bad channels
                    if chan < CMreg[r]:
                        if chan not in Rbad_in_reg[r]:
                            temp_med.append(subtracted_event[chan])
                        else: temp_med.append(-10.0)
                    #find CM
                    else:                         
                        #exclude max channel
                        if r==max_reg:
                            t = max_chan-CMreg[r-1]
                            del temp_med[t]
                        
                            #and its neighbours (2 on both sides)
                            for i in range(1,3):
                                if max_chan+i<CMreg[r]:
                                    del temp_med[t]
                            
                            for i in range(1,3):
                                if max_chan-i>CMreg[r-1]:
                                    del temp_med[t-i]

                        #median of cm
                        while -10.0 in temp_med: temp_med.remove(-10.0)
                        cm_temp_med = median(temp_med)
                        for j in range(CMreg[r-1],CMreg[r]): 
                            CMmed.Fill(j,cm_temp_med)
                            cm_med.append(cm_temp_med)
                            
                        CMDist.Fill(cm_temp_med)
                        
                        #collect the current data for next cm region
                        if chan!=chan_end+1:
                            temp_med=[]
                            temp_med.append(subtracted_event[chan])
                        r+=1
                        
                #if kk==0: print cm
                #cm_med index from 0 to nchan
                max_chan_cm = max_chan - chan_start
                #append last member to avoid index out of range, 
                #it will not be use because the condition max_chan+nr<CMreg[max_reg] in the 2nd while loop
                cm_med.append(cm_med[chan_end-chan_start])            
                
                #####find signal and counting hit strip
                tot_signal2 = subtracted_event[max_chan] - cm_med[max_chan_cm]
                
                #(3.2) real cut: max_chan > 5*noise
                if tot_signal2 < 5*NoiCM.GetBinContent(max_chan+1): temp_med=[]; event_data=[]; continue #print 'skip2';

                tot_noise = R.pow(NoiCM.GetBinContent(max_chan+1),2)                 
                
                #neighbours cut >2*noise
                nl=1; nr=1   #count strips n_left, n_right of the max strip
                while subtracted_event[max_chan-nl]-cm_med[max_chan_cm-nl] > NoiCM.GetBinContent(max_chan-nl+1) and max_chan-nl>chan_start: #max_chan-nl>=CMreg[max_reg-1]: 
                    if max_chan-nl not in Rbad_in_reg[max_reg]:    
                        tot_signal2 += subtracted_event[max_chan-nl] - cm_med[max_chan_cm-nl]
                        tot_noise += R.pow(NoiCM.GetBinContent(max_chan-nl+1),2)
                    nl+=1
                    if nl==3: break
                
                #print max_chan_cm+nr
                while subtracted_event[max_chan+nr]-cm_med[max_chan_cm+nr]> NoiCM.GetBinContent(max_chan+nr+1) and max_chan+nr<chan_end: #max_chan+nr<CMreg[max_reg]:  
                    #if max_chan_cm+nr == 15: print 'in'
                    if max_chan+nr not in Rbad_in_reg[max_reg]: 
                        tot_signal2 += subtracted_event[max_chan+nr] - cm_med[max_chan_cm+nr]
                        tot_noise += R.pow(NoiCM.GetBinContent(max_chan+nr+1),2)
                    nr+=1
                    #print max_chan_cm+nr
                    if nr==3: break
                    
                #number of hit strips = max+(max+-)
                hitstrip = 1+nl+nr-2
                HitStrip.Fill(hitstrip)
                
                #total signal = raw - ped - cm
                SignalHist.Fill(tot_signal2)
                
                if hitstrip <=10:
                
                    # even strip = double metal
                    # case max = DM
                    left = subtracted_event[max_chan-1] - cm_med[max_chan_cm-1]
                    right = subtracted_event[max_chan+1] - cm_med[max_chan_cm+1]
                    if 1==1:#max_chan%2 == 0: 
                        p1 = subtracted_event[max_chan] - cm_med[max_chan_cm]
                        if left > right: p2 = left
                        else: p2 = right
                        #if nl ==2: p2 = subtracted_event[max_chan-1] - cm_med[max_chan_cm-1]
                        #elif nr ==2: p2 = subtracted_event[max_chan+1] - cm_med[max_chan_cm+1]
                        #else: p2 = 0
                        print 'DM ', nl,' ', p1, ' ',p2
                        
                    # side = DM
                   # else: 
                    #    p2 = subtracted_event[max_chan] - cm_med[max_chan_cm]
                     #   if left > right: p1 = left
                      #  else: p1 = right
                      #  #if nl ==2: p1 = subtracted_event[max_chan-1] - cm_med[max_chan_cm-1]
                      #  #elif nr ==2: p1 = subtracted_event[max_chan+1] - cm_med[max_chan_cm+1]
                      #  #else: p1 = 0
                      #  print 'NODM ', nl,' ', p1, ' ',p2
                 
                    eta = p1/(p1+p2)
                    print eta
                    Eta.Fill(eta)
####11111
                
                if kk==-1 and hitstrip == 1: kk=0   
                if kk==0:
                    print max_chan,' ',subtracted_event[max_chan],' ',cm_med[max_chan_cm],' ',subtracted_event[max_chan] - cm_med[max_chan_cm]
                    print tot_signal2,' ', tot_noise,' ', tot_signal2/tot_noise
                    #
                    kk+=1
                        
                #for new line
                temp = 0
                event_data = []

    data_file.close()
    
    print 'skip :',skip_count, ' edge: ',edge_count
    
    for i in range(nchan): 
        NoiCMdat2.Fill(i,NoiSig2.GetBinError(i+1)*R.sqrt(NoiSig2.GetBinEntries(i+1)))
        NoiCMPrePed.Fill(i,NoiCM.GetBinContent(i+1+chan_start))
    
    NoiCMcompare = R.TCanvas('CMsubNoi (Data Vs PrePed)','CM subtracted Noise',600,400)
    NoiCMdat2.SetTitle('CM subtracted noise (Data Vs PrePed)')
    NoiCMPrePed.SetLineColor(3)
    NoiCMdat2.SetLineColor(2)
    NoiCMdat2.Draw()
    NoiCMPrePed.Draw('same')

    label = R.TLegend(.9,.9,.6,.7)
    label.SetFillColor(0)
    label.AddEntry(NoiCMPrePed,'PrePed CMsub Noise ','l')
    label.AddEntry(NoiCMdat2,'Data CMsub Noise (Median CM)','l')
    label.Draw()
    
    for i in range(nchan):
        HitEntries.Fill(i,stripSig[i].GetEntries())
    
    #Saves the Pedestal to the RootFile
    if RFile_name != '':
        RFile = R.TFile(RFile_name,'UPDATE')
        Eta.Write()
        
        #Sig_Data2.Write()
        #Sig_Data3.Write()
        #NoiCMcompare.Write()
        #NoiCMdat2.Write()
        #CMDist.Write()
        #HitStrip.Write()
        #SignalHist.Write()
        #SignalREF.Write()
        #SN.Write()
        #SNn.Write()
        #if dd: 
        #    SNd.Write()
        #    SignalDL.Write()
        #HitEntries.Write()
        #for i in range(nchan):
        #    stripSig[i].Write()
        #    stripSN[i].Write()
        RFile.Close()   
		
# 2013/11/8 -- Nanta
# get signal from Data file
# signal = Raw - Ped - CM
def get_signal2(file_name, chan_start, chan_end, Ped, inCMreg, bad_chans, NoiCM,  title, RFile_name, scale = 1, extra = None, start = 10.0):

    print 'In get_signal2(): Get Signal...'
    if extra == None: extra = title

    #find CMreg in the (start_chan,end_chan)region
    if chan_start!=inCMreg[0] or chan_end+1 != inCMreg[len(inCMreg)-1]: 
        CMreg = get_CMreg(inCMreg,chan_start,chan_end)
        print 'in'
        
    else: CMreg = list(inCMreg)
    
    #find bad channel in the (start_chan,end_chan)region
    Rbad_chans = get_bad_chan_in_region(bad_chans, chan_start, chan_end)
    Rbad_chan_plus = find_bad_chan2_plus(Rbad_chans)
    Rbad_in_reg = sort_bad_chan_into_reg(inCMreg,Rbad_chans)
    
    data_file = open(file_name,'r')

    nchan = abs(chan_end-chan_start)+1
    #print chan_start,' ',chan_end,' ',nchan

    noise = [Ped.GetBinError(i+1)*R.sqrt(Ped.GetBinEntries(i+1)) for i in range(512)]
    #for i in range(chan_start,chan_end+1): NoiseDist.Fill(noise[i])

    HitStrip = R.TH1F('Hit Dist '+extra,'Hit Distribution',10,0,10)
    HitStrip.SetOption('hist')
    HitStrip.GetXaxis().SetTitle('# Hit strips')
    #HitStrip.GetYaxis().SetTitle('Entries')  

    #CM(Common mode noise) from signal data(in range chan_start,chan_end)
    #CM = R.TH2D('Data CM '+title,'Data CM '+title,nchan,chan_start,chan_end+1,150,-15,15)
#    CM = R.TProfile('Data CM '+title,'Data CM '+title,nchan,chan_start,chan_end+1)
#    CM.Sumw2()
#    CM.SetOption('colz')
#    CM.GetXaxis().SetTitle('APV Channel')
#    CM.GetYaxis().SetTitle('CM [ADC count]')
    
    CMmed = R.TProfile('Data CMmed '+title,'Data CMmed '+title,nchan,chan_start,chan_end+1)
    CMmed.Sumw2()
    CMmed.SetOption('colz')
    CMmed.GetXaxis().SetTitle('APV Channel')
    CMmed.GetYaxis().SetTitle('CM [ADC count]')

    #CM distribution 
    CMDist = R.TH1F('DataCM Dist'+extra,'DataCM Distribution '+extra, 40, -5*scale, 5*scale)
    #CMDist.Sumw2()
    CMDist.SetOption('hist')
    CMDist.GetXaxis().SetTitle('Common Mode Noise [ADC]')
    
    #total signal
    SignalHist = R.TH1D('Signal '+extra,extra + ' Signal',220, 0, 220*scale)
    SignalHist.Sumw2()
    SignalHist.SetOption('hist')
    SignalHist.GetXaxis().SetTitle('Signal [ADC Counts]')
    SignalHist.GetYaxis().SetTitle('#Events')
    
    # Sig_Data = raw - ped -cm of each channel with Mean cm
#    Sig_Data = R.TProfile(extra + ' Data',extra + ' Data',nchan, 0, nchan)
#    Sig_Data.Sumw2()
#    Sig_Data.SetOption('colz')
#    Sig_Data.GetXaxis().SetTitle(extra+' Channel')
#    Sig_Data.GetYaxis().SetTitle('Avg. signal [ADC count]')
    
    #Sig_Data with Median cm
    Sig_Data2 = R.TProfile(extra + ' Data2',extra + ' Data2(with Median CM)',nchan, 0, nchan)
    Sig_Data2.Sumw2()
    Sig_Data2.SetOption('colz')
    Sig_Data2.GetXaxis().SetTitle(extra+' Channel')
    Sig_Data2.GetYaxis().SetTitle('Avg. signal [ADC count]')
    
    #signal from strips with no hit for calculating noise
#    NoiSig = R.TProfile('Data NoiSig' + title,'Data Noise Signal ' + title,nchan,0,nchan)
#    NoiSig.Sumw2() #Calculates TRUE average
#    NoiSig.SetOption('colz')
#    NoiSig.GetXaxis().SetTitle('APV Channel')
#    NoiSig.GetYaxis().SetTitle('Avg. signal [ADC count]')
    
    #with Median cm
    NoiSig2 = R.TProfile('Data NoiSig2' + title,'Data Noise Signal2 ' + title,nchan,0,nchan)
    NoiSig2.Sumw2() #Calculates TRUE average
    NoiSig2.SetOption('colz')
    NoiSig2.GetXaxis().SetTitle('APV Channel')
    NoiSig2.GetYaxis().SetTitle('Avg. signal [ADC count]')
    
    #CM subtracted noise from data
#    NoiCMdat = R.TProfile('DataCMsub Noise '+title,'CM subtracted Noise '+title,nchan,0,nchan)
#    NoiCMdat.GetXaxis().SetTitle('APV Channel')
#    NoiCMdat.GetYaxis().SetTitle('CM subtracted Noise [ADC count]')
    
    #with Median cm
    NoiCMdat2 = R.TProfile('DataCMsub Noise2 '+title,'CM subtracted Noise '+title,nchan,0,nchan)
    NoiCMdat2.GetXaxis().SetTitle('APV Channel')
    NoiCMdat2.GetYaxis().SetTitle('CM subtracted Noise [ADC count]')
    
  #  NoiCMdatDist = R.TH1F('DataCMsub Noise Dist '+extra,'CM subtracted Noise distribution '+title,80,0,5)
  #  NoiCMdatDist.SetOption('hist')
  #  NoiCMdatDist.GetXaxis().SetTitle('Noise Distribution')
    
    NoiCMPrePed = R.TProfile('PrePedCMsub Noise '+title,'CM subtracted Noise '+title,nchan,0,nchan)
    NoiCMPrePed.GetXaxis().SetTitle('APV Channel')
    NoiCMPrePed.GetYaxis().SetTitle('CM subtracted Noise [ADC count]')
    
    SamSignal = R.TProfile('Sample Signal ','Sample Signal',512,0,512)
    SamSignal.SetOption('colz')
    SamSignal.GetXaxis().SetTitle('APV Channel')
    SamSignal.GetYaxis().SetTitle('Avg. signal [ADC count]')  

    SamSignal2 = R.TProfile('Sample Signal2 ','Sample Signal',512,0,512)
    SamSignal2.SetOption('colz')
    SamSignal2.GetXaxis().SetTitle('APV Channel')
    SamSignal2.GetYaxis().SetTitle('Avg. signal [ADC count]') 

    SamSignal3 = R.TProfile('Sample Signal3 ','Sample Signal',512,0,512)
    SamSignal3.SetOption('colz')
    SamSignal3.GetXaxis().SetTitle('APV Channel')
    SamSignal3.GetYaxis().SetTitle('Avg. signal [ADC count]') 
    
    SamSignal4 = R.TProfile('Sample Signal4 ','Sample Signal',512,0,512)
    SamSignal4.SetOption('colz')
    SamSignal4.GetXaxis().SetTitle('APV Channel')
    SamSignal4.GetYaxis().SetTitle('Avg. signal [ADC count]') 
    
    #signal to noise ratio
    SN = R.TH1D(extra + ' SN',extra + ' Signal to Noise ratio',160, 0, 80)
    SN.Sumw2()
    SN.SetOption('hist')
    SN.GetXaxis().SetTitle('Signal to noise ratio')
    SN.GetYaxis().SetTitle('Entries')
    
    event_data = [] #stores data from 512 channels of 1 event
    event = 0 #Counts the number of events ~ number of lines with data
    kk=-1
    for line in data_file:
        #Only looks at lines with data in them
        if line.count(',') > 3:
            event += 1 #increments the event count
            if event % 4000 == 0: print event/4 #Prints status
            #APV events
            full_event = [float(x) for x in line.replace('\r\t','').split('\t')[-1].split(',')]
            #scale and store all 4 APVs
            if scale != 1: event_data += [x*192000.0/full_event[-1] for x in full_event[12:-1]]
            else: event_data += full_event[12:-1]

            if event % 4 == 0:

                subtracted_event = [(event_data[i] - Ped.GetBinContent(i+1)) for i in range(len(event_data))]
                
                #max channel in the input region 
                #(1) not include bad chan and their neighbours for max selection
                for i in Rbad_chan_plus: subtracted_event[i] -= 100  
                max_chan = subtracted_event.index(max(subtracted_event[chan_start:chan_end+1]))
                
                #(2) not include edge
                if max_chan==chan_start or max_chan==chan_end: event_data=[]; continue
                
                #(3.1) (coarse screen) not include low signal < *Raw_noise
                if subtracted_event[max_chan] < 2*noise[max_chan]: event_data=[]; continue # print 'skip1';
                    
                for i in Rbad_chan_plus: subtracted_event[i] += 100 
                
                #find the region of max channel
                max_reg = 1
                if len(CMreg)!=2: max_reg = find_reg_of_chan(CMreg,max_chan); #print max_reg
                
                #####find CM
#                cm=[]
#                temp = 0
                cm_med=[]
                temp_med=[]
                r=1  #region index
 #               nc=0 #number of channels in CM region
                for chan in range(chan_start,chan_end+2):
                
                    #add all channels in the region except bad channels
                    if chan < CMreg[r]:
                        if chan not in Rbad_in_reg[r]:
 #                           temp += subtracted_event[chan]
                            temp_med.append(subtracted_event[chan])
 #                           nc +=1
                        else: temp_med.append(-10.0)
                    #find CM
                    else:                         
                        #exclude max channel
                        if r==max_reg:
 #                           temp -= subtracted_event[max_chan]
                            t = max_chan-CMreg[r-1]
                            #print r,' ',nc,' ',max_chan, ' ', chan,' ',t
                            #print temp_med
                            del temp_med[t]
                            #print temp_med
 #                           nc-=1
                        
                            #and its neighbours (2 on both sides)
                            for i in range(1,3):
                                if max_chan+i<CMreg[r]:
 #                                   temp -= subtracted_event[max_chan+i]
                                    del temp_med[t]
 #                                   nc-=1
                            
                            for i in range(1,3):
                                if max_chan-i>CMreg[r-1]:
 #                                   temp -= subtracted_event[max_chan-i]
                                    del temp_med[t-i]
 #                                   nc-=1
                                    
                            #print temp_med
                        #print r,' ',nc,' ',chan,' ',temp
                        #mean cm
 #                       if nc!=0: cm_temp = temp/nc
 #                       else: print 'oops1 '; temp = subtracted_event[chan]; nc=0; r+=1; continue
                        #median of cm
                        while -10.0 in temp_med: temp_med.remove(-10.0)
                        cm_temp_med = median(temp_med)
                        for j in range(CMreg[r-1],CMreg[r]): 
 #                           CM.Fill(j,cm_temp)
 #                           cm.append(cm_temp)
                            CMmed.Fill(j,cm_temp_med)
                            cm_med.append(cm_temp_med)
                            
                        CMDist.Fill(cm_temp_med)
                        
                        #collect the current data for next cm region
                        if chan!=chan_end+1:
 #                           temp = subtracted_event[chan]
 #                           nc=1
                            temp_med=[]
                            temp_med.append(subtracted_event[chan])
                        r+=1
                        
                #if kk==0: print cm
                max_chan_cm = max_chan - chan_start
                #append last member to avoid index out of range, 
                #it will not be use because the condition max_chan+nr<CMreg[max_reg] in the 2nd while loop
                cm_med.append(cm_med[chan_end-chan_start])            
                
                #####find signal and counting hit strip
 #               tot_signal = subtracted_event[max_chan] - cm[max_chan_cm]
                tot_signal2 = subtracted_event[max_chan] - cm_med[max_chan_cm]
                
                #(3.2) real cut: max_chan > 5*noise
                if tot_signal2 < 5*NoiCM.GetBinContent(max_chan+1): temp_med=[]; event_data=[]; continue #print 'skip2';

                tot_noise = R.pow(NoiCM.GetBinContent(max_chan+1),2)                 
                
                #neighbours cut >2*noise
                nl=1; nr=1   #count strips n_left, n_right of the max strip
                while subtracted_event[max_chan-nl]-cm_med[max_chan_cm-nl] > 2*NoiCM.GetBinContent(max_chan-nl+1) and max_chan-nl>chan_start: #max_chan-nl>=CMreg[max_reg-1]: 
                    if max_chan-nl not in Rbad_in_reg[max_reg]:    
 #                       tot_signal += subtracted_event[max_chan-nl] - cm[max_chan_cm-nl]
                        tot_signal2 += subtracted_event[max_chan-nl] - cm_med[max_chan_cm-nl]
                        tot_noise += R.pow(NoiCM.GetBinContent(max_chan-nl+1),2)
                    nl+=1
                    if nl==3: break
                
                #print max_chan_cm+nr
                while subtracted_event[max_chan+nr]-cm_med[max_chan_cm+nr]> 2*NoiCM.GetBinContent(max_chan+nr+1) and max_chan+nr<chan_end: #max_chan+nr<CMreg[max_reg]:  
                    #if max_chan_cm+nr == 15: print 'in'
                    if max_chan+nr not in Rbad_in_reg[max_reg]: 
 #                       tot_signal += subtracted_event[max_chan+nr] - cm[max_chan_cm+nr]
                        tot_signal2 += subtracted_event[max_chan+nr] - cm_med[max_chan_cm+nr]
                        tot_noise += R.pow(NoiCM.GetBinContent(max_chan+nr+1),2)
                    nr+=1
                    #print max_chan_cm+nr
                    if nr==3: break
                    
                #number of hit strips = max+(max+-)
                hitstrip = 1+nl+nr-2
                HitStrip.Fill(hitstrip)
                if kk==-1 and cm_med[max_chan_cm-2] >2: kk=0
                #if kk==1 and hitstrip ==4: kk=3
                
                #total signal = raw - ped - cm
                SignalHist.Fill(tot_signal2)
                
                #signal to calculate noise
                for i in range(0,max_chan-nl-chan_start): 
 #                   NoiSig.Fill(i,subtracted_event[i+chan_start] - cm[i])
                    NoiSig2.Fill(i,subtracted_event[i+chan_start] - cm_med[i])
                for i in range(max_chan+nr+1-chan_start,nchan): 
 #                   NoiSig.Fill(i,subtracted_event[i+chan_start] - cm[i])
                    NoiSig2.Fill(i,subtracted_event[i+chan_start] - cm_med[i])
                
                for i in range(chan_start,chan_end+1): 
 #                   Sig_Data.Fill(i-chan_start,subtracted_event[i] - cm[i-chan_start])
                    Sig_Data2.Fill(i-chan_start,subtracted_event[i] - cm_med[i-chan_start])
                
                if kk==0:
                    print max_chan,' ',subtracted_event[max_chan],' ',cm_med[max_chan_cm],' ',subtracted_event[max_chan] - cm_med[max_chan_cm]
                    for i in range(chan_start,chan_end+1): SamSignal.Fill(i,event_data[i])
                    for i in range(chan_start,chan_end+1): SamSignal2.Fill(i,subtracted_event[i])
                    for i in range(chan_start,chan_end+1): SamSignal3.Fill(i,subtracted_event[i] - cm_med[i-chan_start])
                    kk+=1

                if kk==3:
                    print max_chan,' ',subtracted_event[max_chan],' ',cm_med[max_chan_cm],' ',subtracted_event[max_chan] - cm_med[max_chan_cm]
                 #   for i in range(chan_start,chan_end+1): SamSignal3.Fill(i,subtracted_event[i] - cm_med[i-chan_start])
 #                   for i in range(chan_start,chan_end+1): SamSignal4.Fill(i,subtracted_event[i])
          #          for i in range(chan_start,chan_end+1): SamSignal3.Fill(i-chan_start,NoiSig.GetBinContent(i+1-chan_start))
                    kk+=1
                    
                    
                #signal to noise ratio
                
                SN.Fill(tot_signal2/R.sqrt(tot_noise))

                #for new line
                temp = 0
                event_data = []

    data_file.close()
    
    for i in range(nchan): 
#        NoiCMdat.Fill(i,NoiSig.GetBinError(i+1)*R.sqrt(NoiSig.GetBinEntries(i+1)))
        NoiCMdat2.Fill(i,NoiSig2.GetBinError(i+1)*R.sqrt(NoiSig2.GetBinEntries(i+1)))
        #NoiCMdatDist.Fill(NoiCMdat.GetBinContent(i+1))
        NoiCMPrePed.Fill(i,NoiCM.GetBinContent(i+1+chan_start))
    
    NoiCMcompare = R.TCanvas('CMsubNoi (Data Vs PrePed)','CM subtracted Noise',600,400)
    NoiCMdat2.SetTitle('CM subtracted noise (Data Vs PrePed)')
    NoiCMPrePed.SetLineColor(3)
    NoiCMdat2.SetLineColor(2)
    NoiCMdat2.Draw()
    NoiCMPrePed.Draw('same')
#    NoiCMdat2.Draw('same')

    label = R.TLegend(.9,.9,.6,.7)
    label.SetFillColor(0)
#    label.AddEntry(NoiCMdat,'Data CMsub Noise (Mean CM)','l')
    label.AddEntry(NoiCMPrePed,'PrePed CMsub Noise ','l')
    label.AddEntry(NoiCMdat2,'Data CMsub Noise (Median CM)','l')
    label.Draw()
    
    Signal_compare = R.TCanvas('sigVsraw-ped','signal',600,400)
    SamSignal2.SetTitle('')
    SamSignal2.SetLineColor(2)
    SamSignal2.Draw()
    SamSignal3.Draw('same')

    label2 = R.TLegend(.9,.9,.6,.7)
    label2.SetFillColor(0)
#    label.AddEntry(NoiCMdat,'Data CMsub Noise (Mean CM)','l')
    label2.AddEntry(SamSignal2,'Raw-Red','l')
    label2.AddEntry(SamSignal3,'Raw-Ped-CM','l')
    label.Draw()
    
    

    #compare mean CM and median CM
#    CMcompare = R.TCanvas('CM(mean vs med) '+extra,'mean CM Vs Median CM '+extra,600,400)
#    CM.SetTitle('Mean CM Vs Median CM')
#    CMmed.SetLineColor(2)
#    CM.Draw()
#    CMmed.Draw('same')
    
#    label2 = R.TLegend(.9,.9,.6,.7)
#    label2.SetFillColor(0)
#    label2.AddEntry(CM,'Mean CM','l')
#    label2.AddEntry(CMmed,'Median CM','l')
#    label2.Draw()
    
    #Saves the Pedestal to the RootFile
    if RFile_name != '':
        RFile = R.TFile(RFile_name,'UPDATE')
        #CM.Write()
#        Sig_Data.Write()
        Sig_Data2.Write()
        NoiCMcompare.Write()
#        CMcompare.Write()
        CMDist.Write()
        HitStrip.Write()
        SignalHist.Write()
        SN.Write()
        #NoiCMdat.Write()
        #NoiCMdatDist.Write()
        SamSignal.Write()
        SamSignal2.Write()
        SamSignal3.Write()
#        SamSignal4.Write()
        #Noise.Write()
        RFile.Close()
       
    # fit Signal
    hist_name = 'Signal '+ extra
    print hist_name
    i = start

    R.gROOT.ProcessLine('LandauFit("' + RFile_name + '","' + hist_name + '","' + extra + '",'+str(scale)+','+str(i-1)+')')
    RFile = R.TFile(RFile_name,'READ')
    chi2_before = RFile.Get(hist_name).GetFunction(extra+'_Func').GetChisquare()
    RFile.Close()

    R.gROOT.ProcessLine('LandauFit("' + RFile_name + '","' + hist_name + '","' + extra + '",'+str(scale)+','+str(i+1)+')')
    RFile = R.TFile(RFile_name,'READ')
    chi2_after = RFile.Get(hist_name).GetFunction(extra+'_Func').GetChisquare()
    RFile.Close()

    R.gROOT.ProcessLine('LandauFit("' + RFile_name + '","' + hist_name + '","' + extra + '",'+str(scale)+','+str(i)+')')
    RFile = R.TFile(RFile_name,'READ')
    chi2 = RFile.Get(hist_name).GetFunction(extra+'_Func').GetChisquare()
    RFile.Close()
    print chi2_before, chi2, chi2_after

    if (chi2 > chi2_before and chi2 < chi2_after) or (chi2 > chi2_before and chi2 > chi2_after and chi2_before < chi2_after):
        while chi2 >= chi2_before or chi2 > chi2_after or chi2 > 460:
            i -= 1.0
            chi2_after = chi2
            chi2 = chi2_before

            R.gROOT.ProcessLine('LandauFit("' + RFile_name + '","' + hist_name + '","' + extra + '",'+str(scale)+','+str(i)+')')
            RFile = R.TFile(RFile_name,'READ')
            chi2_before = RFile.Get(hist_name).GetFunction(extra+'_Func').GetChisquare()
            print chi2, RFile.Get(hist_name).GetFunction(extra+'_Func').GetMaximumX(), i
            RFile.Close()
        i += 1.0

    elif (chi2 < chi2_before and chi2 > chi2_after) or (chi2 > chi2_before and chi2 > chi2_after and chi2_before > chi2_after):
        while chi2 > chi2_before or chi2 >= chi2_after or chi2 > 460:
            i += 1.0
            chi2_before = chi2
            chi2 = chi2_after
        
            R.gROOT.ProcessLine('LandauFit("' + RFile_name + '","' + hist_name + '","' + extra + '",'+str(scale)+','+str(i)+')')
            RFile = R.TFile(RFile_name,'READ')
            chi2_after = RFile.Get(hist_name).GetFunction(extra+'_Func').GetChisquare()
            print chi2, RFile.Get(hist_name).GetFunction(extra+'_Func').GetMaximumX(), i
            RFile.Close()
        i -= 1.0

    R.gROOT.ProcessLine('LandauFit("' + RFile_name + '","' + hist_name + '","' + extra + '",'+str(scale)+','+str(i+1)+')')
    RFile = R.TFile(RFile_name,'READ')
    chi2_after = RFile.Get(hist_name).GetFunction(extra+'_Func').GetChisquare()
    print chi2, RFile.Get(hist_name).GetFunction(extra+'_Func').GetMaximumX(), i
    RFile.Close()

    return SignalHist    
    
#2013/11/3 -- Nanta
#2013/11/8 -- add double metal selection for Signal to Noise ratio 
def get_signalDoubleMetal(file_name, chan_start, chan_end, Ped, inCMreg, bad_chans, NoiCM,  title, RFile_name, dd=0, scale = 1, extra = None, start = 10.0):

    print 'Get Signal...'
    if extra == None: extra = title
	
    #find CMreg in the (start_chan,end_chan)region
    if chan_start!=inCMreg[0] or chan_end+1 != inCMreg[len(inCMreg)-1]: 
        CMreg = get_CMreg(inCMreg,chan_start,chan_end)
        print 'in'
        
    else: CMreg = list(inCMreg)

    #find bad channel in the (start_chan,end_chan)region
    Rbad_chans = get_bad_chan_in_region(bad_chans, chan_start, chan_end)
    Rbad_chan_plus = find_bad_chan2_plus(Rbad_chans)
    Rbad_in_reg = sort_bad_chan_into_reg(CMreg,Rbad_chans)
        
    data_file = open(file_name,'r')

    nchan = abs(chan_end-chan_start)+1
    #print chan_start,' ',chan_end,' ',nchan

    noise = [Ped.GetBinError(i+1)*R.sqrt(Ped.GetBinEntries(i+1)) for i in range(512)]
    #for i in range(chan_start,chan_end+1): NoiseDist.Fill(noise[i])

    HitStrip = R.TH1F('Hit Dist '+extra,'Hit Distribution',10,0,10)
    HitStrip.SetOption('hist')
    HitStrip.GetXaxis().SetTitle('# Hit strips')
    #HitStrip.GetYaxis().SetTitle('Entries')  

    #CM(Common mode noise) from signal data(in range chan_start,chan_end)   
    CMmed = R.TProfile('Data CMmed '+title,'Data CMmed '+title,nchan,chan_start,chan_end+1)
    CMmed.Sumw2()
    CMmed.SetOption('colz')
    CMmed.GetXaxis().SetTitle('APV Channel')
    CMmed.GetYaxis().SetTitle('CM [ADC count]')

    #CM distribution 
    CMDist = R.TH1F('DataCM Dist '+extra,'DataCM Distribution '+extra, 40, -5*scale, 5*scale)
    #CMDist.Sumw2()
    CMDist.SetOption('hist')
    CMDist.GetXaxis().SetTitle('Common Mode Noise [ADC]')
    
    #total signal
    SignalHist = R.TH1D('Signal '+extra,extra + ' Signal',120, 0, 120*scale)
    SignalHist.Sumw2()
    SignalHist.SetOption('hist')
    SignalHist.GetXaxis().SetTitle('Signal [ADC Counts]')
    SignalHist.GetYaxis().SetTitle('#Events')
    
    # read only signal from max-signal strips with double layer (even strips)
    SignalDL = R.TH1D(extra + ' DL_Signal',extra+' DL_Signal',120,0,120*scale)
    SignalDL.Sumw2()
    SignalDL.SetOption('hist')
    SignalDL.GetXaxis().SetTitle('Signal [ADC Counts]')
    SignalDL.GetYaxis().SetTitle('#Events')

    # read only signal from max-signal strips with NO double layer (Reference) (odd strips)
    SignalREF = R.TH1D(extra +' NODL_Signal',extra+' NODL_Signal',120,0,120*scale)
    SignalREF.Sumw2()
    SignalREF.SetOption('hist')
    SignalREF.GetXaxis().SetTitle('Signal [ADC Counts]')
    SignalREF.GetYaxis().SetTitle('#Events')
    
    # Sig_Data = raw - ped -cm of each channel 
    #Sig_Data with Median cm
    Sig_Data2 = R.TProfile(extra + ' Data2',extra + ' Data2(with Median CM)',nchan, 0, nchan)
    Sig_Data2.Sumw2()
    Sig_Data2.SetOption('colz')
    Sig_Data2.GetXaxis().SetTitle(extra+' Channel')
    Sig_Data2.GetYaxis().SetTitle('Avg. signal [ADC count]')
    
    #signal from strips with no hit for calculating noise
    #with Median cm
    NoiSig2 = R.TProfile('Data NoiSig2' + title,'Data Noise Signal2 ' + title,nchan,0,nchan)
    NoiSig2.Sumw2() #Calculates TRUE average
    NoiSig2.SetOption('colz')
    NoiSig2.GetXaxis().SetTitle('APV Channel')
    NoiSig2.GetYaxis().SetTitle('Avg. signal [ADC count]')
    
    #CM subtracted noise from data
    #with Median cm
    NoiCMdat2 = R.TProfile('DataCMsub Noise2 '+title,'CM subtracted Noise '+title,nchan,0,nchan)
    NoiCMdat2.GetXaxis().SetTitle('APV Channel')
    NoiCMdat2.GetYaxis().SetTitle('CM subtracted Noise [ADC count]')
    
  #  NoiCMdatDist = R.TH1F('DataCMsub Noise Dist '+extra,'CM subtracted Noise distribution '+title,80,0,5)
  #  NoiCMdatDist.SetOption('hist')
  #  NoiCMdatDist.GetXaxis().SetTitle('Noise Distribution')
    
    NoiCMPrePed = R.TProfile('PrePedCMsub Noise_part '+title,'CM subtracted Noise '+title,nchan,0,nchan)
    NoiCMPrePed.GetXaxis().SetTitle('APV Channel')
    NoiCMPrePed.GetYaxis().SetTitle('CM subtracted Noise [ADC count]')
    
    SamSignal = R.TProfile('Sample Signal ','Sample Signal',512,0,512)
    SamSignal.SetOption('colz')
    SamSignal.GetXaxis().SetTitle('APV Channel')
    SamSignal.GetYaxis().SetTitle('Avg. signal [ADC count]')  

    SamSignal2 = R.TProfile('Sample Signal2 ','Sample Signal',512,0,512)
    SamSignal2.SetOption('colz')
    SamSignal2.GetXaxis().SetTitle('APV Channel')
    SamSignal2.GetYaxis().SetTitle('Avg. signal [ADC count]') 
    
    SamSignal3 = R.TProfile('Sample Signal3 ','Sample Signal',512,0,512)
    SamSignal3.SetOption('colz')
    SamSignal3.GetXaxis().SetTitle('APV Channel')
    SamSignal3.GetYaxis().SetTitle('Avg. signal [ADC count]') 

    #signal to noise ratio
    SN = R.TH1D(extra + ' SN',extra + ' Signal to Noise ratio',200, 0, 100)
    SN.Sumw2()
    SN.SetOption('hist')
    SN.GetXaxis().SetTitle('Signal to noise ratio')
    SN.GetYaxis().SetTitle('Entries')

    SNn = R.TH1D(extra + ' SN no double',extra + ' Signal to Noise ratio (No Double metal)',200, 0, 100)
    SNn.Sumw2()
    SNn.SetOption('hist')
    SNn.GetXaxis().SetTitle('Signal to noise ratio')
    SNn.GetYaxis().SetTitle('Entries')
    
    if dd:
        SNd = R.TH1D(extra + ' SN double',extra + ' Signal to Noise ratio (Double metal)',200, 0, 100)
        SNd.Sumw2()
        SNd.SetOption('hist')
        SNd.GetXaxis().SetTitle('Signal to noise ratio')
        SNd.GetYaxis().SetTitle('Entries')
    
    event_data = [] #stores data from 512 channels of 1 event
    event = 0 #Counts the number of events ~ number of lines with data
    kk=-1
    skip_count = 0
    edge_count = 0
    for line in data_file:
        #Only looks at lines with data in them
        if line.count(',') > 3:
            event += 1 #increments the event count
            if event % 4000 == 0: print event/4 #Prints status
            #APV events
            full_event = [float(x) for x in line.replace('\r\t','').split('\t')[-1].split(',')]
            #scale and store all 4 APVs
            if scale != 1: event_data += [x*192000.0/full_event[-1] for x in full_event[12:-1]]
            else: event_data += full_event[12:-1]

            if event % 4 == 0:

                subtracted_event = [(event_data[i] - Ped.GetBinContent(i+1)) for i in range(len(event_data))]
                
                #max channel in the input region 
                #(1) not include bad chan and their neighbours for max selection
                for i in Rbad_chan_plus: subtracted_event[i] -= 100  
                max_chan = subtracted_event.index(max(subtracted_event[chan_start:chan_end+1]))
                
                #(2) not include edge
                if max_chan==chan_start or max_chan==chan_end: event_data=[]; edge_count +=1; continue
                
                #(3.1) (coarse screen) not include low signal < *Raw_noise
                if subtracted_event[max_chan] < 2*noise[max_chan]: event_data=[]; skip_count +=1; continue # print 'skip1';
                    
                for i in Rbad_chan_plus: subtracted_event[i] += 100 
                
                #find the region of max channel
                max_reg = 1
                if len(CMreg)!=2: max_reg = find_reg_of_chan(CMreg,max_chan); #print max_reg
                
                #####find CM (median CM)
                cm_med=[]
                temp_med=[]
                r=1  #region index
                for chan in range(chan_start,chan_end+2):
                
                    #add all channels in the region except bad channels
                    if chan < CMreg[r]:
                        if chan not in Rbad_in_reg[r]:
                            temp_med.append(subtracted_event[chan])
                        else: temp_med.append(-10.0)
                    #find CM
                    else:                         
                        #exclude max channel
                        if r==max_reg:
                            t = max_chan-CMreg[r-1]
                            del temp_med[t]
                        
                            #and its neighbours (2 on both sides)
                            for i in range(1,3):
                                if max_chan+i<CMreg[r]:
                                    del temp_med[t]
                            
                            for i in range(1,3):
                                if max_chan-i>CMreg[r-1]:
                                    del temp_med[t-i]

                        #median of cm
                        while -10.0 in temp_med: temp_med.remove(-10.0)
                        cm_temp_med = median(temp_med)
                        for j in range(CMreg[r-1],CMreg[r]): 
                            CMmed.Fill(j,cm_temp_med)
                            cm_med.append(cm_temp_med)
                            
                        CMDist.Fill(cm_temp_med)
                        
                        #collect the current data for next cm region
                        if chan!=chan_end+1:
                            temp_med=[]
                            temp_med.append(subtracted_event[chan])
                        r+=1
                        
                #if kk==0: print cm
                max_chan_cm = max_chan - chan_start
                #append last member to avoid index out of range, 
                #it will not be use because the condition max_chan+nr<CMreg[max_reg] in the 2nd while loop
                cm_med.append(cm_med[chan_end-chan_start])            
                
                #####find signal and counting hit strip
                tot_signal2 = subtracted_event[max_chan] - cm_med[max_chan_cm]
                
                #(3.2) real cut: max_chan > 5*noise
                if tot_signal2 < 5*NoiCM.GetBinContent(max_chan+1): temp_med=[]; event_data=[]; continue #print 'skip2';

                tot_noise = R.pow(NoiCM.GetBinContent(max_chan+1),2)                 
                
                #neighbours cut >2*noise
                nl=1; nr=1   #count strips n_left, n_right of the max strip
                while subtracted_event[max_chan-nl]-cm_med[max_chan_cm-nl] > 2*NoiCM.GetBinContent(max_chan-nl+1) and max_chan-nl>chan_start: #max_chan-nl>=CMreg[max_reg-1]: 
                    if max_chan-nl not in Rbad_in_reg[max_reg]:    
                        tot_signal2 += subtracted_event[max_chan-nl] - cm_med[max_chan_cm-nl]
                        tot_noise += R.pow(NoiCM.GetBinContent(max_chan-nl+1),2)
                    nl+=1
                    if nl==3: break
                
                #print max_chan_cm+nr
                while subtracted_event[max_chan+nr]-cm_med[max_chan_cm+nr]> 2*NoiCM.GetBinContent(max_chan+nr+1) and max_chan+nr<chan_end: #max_chan+nr<CMreg[max_reg]:  
                    #if max_chan_cm+nr == 15: print 'in'
                    if max_chan+nr not in Rbad_in_reg[max_reg]: 
                        tot_signal2 += subtracted_event[max_chan+nr] - cm_med[max_chan_cm+nr]
                        tot_noise += R.pow(NoiCM.GetBinContent(max_chan+nr+1),2)
                    nr+=1
                    #print max_chan_cm+nr
                    if nr==3: break
                    
                #number of hit strips = max+(max+-)
                hitstrip = 1+nl+nr-2
                HitStrip.Fill(hitstrip)
                if kk==-1 and cm_med[max_chan_cm-2] >1.5: kk=0
                #if kk==-1 and hitstrip ==2: kk= 0
                if kk==1 and hitstrip ==3: kk=3
                
                #total signal = raw - ped - cm
                SignalHist.Fill(tot_signal2)
                
                #signal to calculate noise
                for i in range(0,max_chan-nl-chan_start): 
                    NoiSig2.Fill(i,subtracted_event[i+chan_start] - cm_med[i])
                for i in range(max_chan+nr+1-chan_start,nchan): 
                    NoiSig2.Fill(i,subtracted_event[i+chan_start] - cm_med[i])
                
                for i in range(chan_start,chan_end+1): 
                    Sig_Data2.Fill(i-chan_start,subtracted_event[i] - cm_med[i-chan_start])
                
                if kk==0:
                    print max_chan,' ',subtracted_event[max_chan],' ',cm_med[max_chan_cm],' ',subtracted_event[max_chan] - cm_med[max_chan_cm]
                    print tot_signal2,' ', R.sqrt(tot_noise),' ', tot_signal2/tot_noise
                    #for i in range(chan_start,chan_end+1): SamSignal.Fill(i,event_data[i])
                    for i in range(chan_start,chan_end+1): SamSignal.Fill(i,subtracted_event[i])
                    #for i in range(chan_start,340): SamSignal3.Fill(i,subtracted_event[i])
                    #for i in range(340,384): SamSignal3.Fill(i,subtracted_event[i]-cm_med[i-chan_start])
                    #for i in range(384,chan_end): SamSignal3.Fill(i,subtracted_event[i])
                    for i in range(chan_start,chan_end+1): SamSignal2.Fill(i,subtracted_event[i] - cm_med[i-chan_start])
                    kk+=1

                if kk==3:
                    print max_chan,' ',subtracted_event[max_chan],' ',cm_med[max_chan_cm],' ',subtracted_event[max_chan] - cm_med[max_chan_cm]
                    print tot_signal2,' ', R.sqrt(tot_noise),' ', tot_signal2/tot_noise
                    for i in range(chan_start,chan_end+1): SamSignal3.Fill(i,subtracted_event[i] - cm_med[i-chan_start])
                    kk+=1
                    
                    
                #signal to noise ratio
                tot_noise = R.sqrt(tot_noise)
                SN.Fill(tot_signal2/tot_noise)
                if hitstrip ==1:
                    if dd:
                        #even strip = double metal
                        if max_chan%2 ==0: 
                            SNd.Fill(tot_signal2/tot_noise)
                            SignalDL.Fill(tot_signal2)
                        else: 
                            SNn.Fill(tot_signal2/tot_noise)
                            SignalREF.Fill(tot_signal2)
                        
                    else: 
                        SNn.Fill(tot_signal2/tot_noise)
                        SignalREF.Fill(tot_signal2)
                        
                #for new line
                temp = 0
                event_data = []

    data_file.close()
    
    print 'skip :',skip_count, ' edge: ',edge_count
    
    for i in range(nchan): 
        NoiCMdat2.Fill(i,NoiSig2.GetBinError(i+1)*R.sqrt(NoiSig2.GetBinEntries(i+1)))
        NoiCMPrePed.Fill(i,NoiCM.GetBinContent(i+1+chan_start))
    
    NoiCMcompare = R.TCanvas('CMsubNoi (Data Vs PrePed)','CM subtracted Noise',600,400)
    NoiCMdat2.SetTitle('CM subtracted noise (Data Vs PrePed)')
    NoiCMPrePed.SetLineColor(3)
    NoiCMdat2.SetLineColor(2)
    NoiCMdat2.Draw()
    NoiCMPrePed.Draw('same')

    label = R.TLegend(.9,.9,.6,.7)
    label.SetFillColor(0)
    label.AddEntry(NoiCMPrePed,'PrePed CMsub Noise ','l')
    label.AddEntry(NoiCMdat2,'Data CMsub Noise (Median CM)','l')
    label.Draw()
    
    #Saves the Pedestal to the RootFile
    if RFile_name != '':
        RFile = R.TFile(RFile_name,'UPDATE')
        Sig_Data2.Write()
        NoiCMcompare.Write()
        CMDist.Write()
        HitStrip.Write()
        SignalHist.Write()
        SignalREF.Write()
        SN.Write()
        SNn.Write()
        if dd: 
            SNd.Write()
            SignalDL.Write()
        #NoiCMdat.Write()
        #NoiCMdatDist.Write()
        SamSignal.Write()
        SamSignal2.Write()
        SamSignal3.Write()
        #SamSignal4.Write()
        #Noise.Write()
        RFile.Close()
       
    # fit Signal
    hist_name = 'Signal '+ extra
    print hist_name
    i = start

    R.gROOT.ProcessLine('LandauFit("' + RFile_name + '","' + hist_name + '","' + extra + '",'+str(scale)+','+str(i-1)+')')
    RFile = R.TFile(RFile_name,'READ')
    chi2_before = RFile.Get(hist_name).GetFunction(extra+'_Func').GetChisquare()
    RFile.Close()

    R.gROOT.ProcessLine('LandauFit("' + RFile_name + '","' + hist_name + '","' + extra + '",'+str(scale)+','+str(i+1)+')')
    RFile = R.TFile(RFile_name,'READ')
    chi2_after = RFile.Get(hist_name).GetFunction(extra+'_Func').GetChisquare()
    RFile.Close()

    R.gROOT.ProcessLine('LandauFit("' + RFile_name + '","' + hist_name + '","' + extra + '",'+str(scale)+','+str(i)+')')
    RFile = R.TFile(RFile_name,'READ')
    chi2 = RFile.Get(hist_name).GetFunction(extra+'_Func').GetChisquare()
    RFile.Close()
    print chi2_before, chi2, chi2_after

    if (chi2 > chi2_before and chi2 < chi2_after) or (chi2 > chi2_before and chi2 > chi2_after and chi2_before < chi2_after):
        while chi2 >= chi2_before or chi2 > chi2_after or chi2 > 460:
            i -= 1.0
            chi2_after = chi2
            chi2 = chi2_before

            R.gROOT.ProcessLine('LandauFit("' + RFile_name + '","' + hist_name + '","' + extra + '",'+str(scale)+','+str(i)+')')
            RFile = R.TFile(RFile_name,'READ')
            chi2_before = RFile.Get(hist_name).GetFunction(extra+'_Func').GetChisquare()
            print chi2, RFile.Get(hist_name).GetFunction(extra+'_Func').GetMaximumX(), i
            RFile.Close()
        i += 1.0

    elif (chi2 < chi2_before and chi2 > chi2_after) or (chi2 > chi2_before and chi2 > chi2_after and chi2_before > chi2_after):
        while chi2 > chi2_before or chi2 >= chi2_after or chi2 > 460:
            i += 1.0
            chi2_before = chi2
            chi2 = chi2_after
        
            R.gROOT.ProcessLine('LandauFit("' + RFile_name + '","' + hist_name + '","' + extra + '",'+str(scale)+','+str(i)+')')
            RFile = R.TFile(RFile_name,'READ')
            chi2_after = RFile.Get(hist_name).GetFunction(extra+'_Func').GetChisquare()
            print chi2, RFile.Get(hist_name).GetFunction(extra+'_Func').GetMaximumX(), i
            RFile.Close()
        i -= 1.0

    R.gROOT.ProcessLine('LandauFit("' + RFile_name + '","' + hist_name + '","' + extra + '",'+str(scale)+','+str(i+1)+')')
    RFile = R.TFile(RFile_name,'READ')
    chi2_after = RFile.Get(hist_name).GetFunction(extra+'_Func').GetChisquare()
    print chi2, RFile.Get(hist_name).GetFunction(extra+'_Func').GetMaximumX(), i
    RFile.Close()

    # fit DLSignal
    if dd:
        hist_name = extra + ' DL_Signal'
        print hist_name
        i = start

        R.gROOT.ProcessLine('LandauFit("' + RFile_name + '","' + hist_name + '","' + hist_name + '",'+str(scale)+','+str(i-1)+')')
        RFile = R.TFile(RFile_name,'READ')
        chi2_before = RFile.Get(extra + ' DL_Signal').GetFunction(hist_name+'_Func').GetChisquare()
        RFile.Close()

        R.gROOT.ProcessLine('LandauFit("' + RFile_name + '","' + hist_name + '","' + hist_name + '",'+str(scale)+','+str(i+1)+')')
        RFile = R.TFile(RFile_name,'READ')
        chi2_after = RFile.Get(extra + ' DL_Signal').GetFunction(hist_name+'_Func').GetChisquare()
        RFile.Close()

        R.gROOT.ProcessLine('LandauFit("' + RFile_name + '","' + hist_name + '","' + hist_name + '",'+str(scale)+','+str(i)+')')
        RFile = R.TFile(RFile_name,'READ')
        chi2 = RFile.Get(extra + ' DL_Signal').GetFunction(hist_name+'_Func').GetChisquare()
        RFile.Close()
        print chi2_before, chi2, chi2_after

        if (chi2 > chi2_before and chi2 < chi2_after) or (chi2 > chi2_before and chi2 > chi2_after and chi2_before < chi2_after):
            while chi2 >= chi2_before or chi2 > chi2_after or chi2 > 460:
                i -= 1.0
                chi2_after = chi2
                chi2 = chi2_before

                R.gROOT.ProcessLine('LandauFit("' + RFile_name + '","' + hist_name + '","' + hist_name + '",'+str(scale)+','+str(i)+')')
                RFile = R.TFile(RFile_name,'READ')
                chi2_before = RFile.Get(extra + ' DL_Signal').GetFunction(hist_name+'_Func').GetChisquare()
                print chi2, RFile.Get(extra + ' DL_Signal').GetFunction(hist_name+'_Func').GetMaximumX(), i
                RFile.Close()
            i += 1.0

        elif (chi2 < chi2_before and chi2 > chi2_after) or (chi2 > chi2_before and chi2 > chi2_after and chi2_before > chi2_after):
            while chi2 > chi2_before or chi2 >= chi2_after or chi2 > 460:
                i += 1.0
                chi2_before = chi2
                chi2 = chi2_after
        
                R.gROOT.ProcessLine('LandauFit("' + RFile_name + '","' + hist_name + '","' + hist_name + '",'+str(scale)+','+str(i)+')')
                RFile = R.TFile(RFile_name,'READ')
                chi2_after = RFile.Get(extra + ' DL_Signal').GetFunction(hist_name+'_Func').GetChisquare()
                print chi2, RFile.Get(extra + ' DL_Signal').GetFunction(hist_name+'_Func').GetMaximumX(), i
                RFile.Close()
            i -= 1.0

        R.gROOT.ProcessLine('LandauFit("' + RFile_name + '","' + hist_name + '","' + hist_name + '",'+str(scale)+','+str(i+1)+')')
        RFile = R.TFile(RFile_name,'READ')
        chi2_after = RFile.Get(extra + ' DL_Signal').GetFunction(hist_name+'_Func').GetChisquare()
        print chi2, RFile.Get(extra + ' DL_Signal').GetFunction(hist_name+'_Func').GetMaximumX(), i
        RFile.Close()
    
    # fit NODLSignal
    hist_name = extra + ' NODL_Signal'
    print hist_name
    i = start

    R.gROOT.ProcessLine('LandauFit("' + RFile_name + '","' + hist_name + '","' + hist_name + '",'+str(scale)+','+str(i-1)+')')
    RFile = R.TFile(RFile_name,'READ')
    chi2_before = RFile.Get(extra + ' NODL_Signal').GetFunction(hist_name+'_Func').GetChisquare()
    RFile.Close()

    R.gROOT.ProcessLine('LandauFit("' + RFile_name + '","' + hist_name + '","' + hist_name + '",'+str(scale)+','+str(i+1)+')')
    RFile = R.TFile(RFile_name,'READ')
    chi2_after = RFile.Get(extra + ' NODL_Signal').GetFunction(hist_name+'_Func').GetChisquare()
    RFile.Close()

    R.gROOT.ProcessLine('LandauFit("' + RFile_name + '","' + hist_name + '","' + hist_name + '",'+str(scale)+','+str(i)+')')
    RFile = R.TFile(RFile_name,'READ')
    chi2 = RFile.Get(extra + ' NODL_Signal').GetFunction(hist_name+'_Func').GetChisquare()
    RFile.Close()
    print chi2_before, chi2, chi2_after

    if (chi2 > chi2_before and chi2 < chi2_after) or (chi2 > chi2_before and chi2 > chi2_after and chi2_before < chi2_after):
        while chi2 >= chi2_before or chi2 > chi2_after or chi2 > 460:
            i -= 1.0
            chi2_after = chi2
            chi2 = chi2_before

            R.gROOT.ProcessLine('LandauFit("' + RFile_name + '","' + hist_name + '","' + hist_name + '",'+str(scale)+','+str(i)+')')
            RFile = R.TFile(RFile_name,'READ')
            chi2_before = RFile.Get(extra + ' NODL_Signal').GetFunction(hist_name+'_Func').GetChisquare()
            print chi2, RFile.Get(extra + ' NODL_Signal').GetFunction(hist_name+'_Func').GetMaximumX(), i
            RFile.Close()
        i += 1.0

    elif (chi2 < chi2_before and chi2 > chi2_after) or (chi2 > chi2_before and chi2 > chi2_after and chi2_before > chi2_after):
        while chi2 > chi2_before or chi2 >= chi2_after or chi2 > 460:
            i += 1.0
            chi2_before = chi2
            chi2 = chi2_after
        
            R.gROOT.ProcessLine('LandauFit("' + RFile_name + '","' + hist_name + '","' + hist_name + '",'+str(scale)+','+str(i)+')')
            RFile = R.TFile(RFile_name,'READ')
            chi2_after = RFile.Get(extra + ' NODL_Signal').GetFunction(hist_name+'_Func').GetChisquare()
            print chi2, RFile.Get(extra + ' NODL_Signal').GetFunction(hist_name+'_Func').GetMaximumX(), i
            RFile.Close()
        i -= 1.0

    R.gROOT.ProcessLine('LandauFit("' + RFile_name + '","' + hist_name + '","' + hist_name + '",'+str(scale)+','+str(i+1)+')')
    RFile = R.TFile(RFile_name,'READ')
    chi2_after = RFile.Get(extra + ' NODL_Signal').GetFunction(hist_name+'_Func').GetChisquare()
    print chi2, RFile.Get(extra + ' NODL_Signal').GetFunction(hist_name+'_Func').GetMaximumX(), i
    RFile.Close()
    
    
    # fit SN double to find MPV (SN=Singal to Noise ratio)
    if dd:    
        hist_name = extra + ' SN double'
        print hist_name
        i = start

        R.gROOT.ProcessLine('LandauFit("' + RFile_name + '","' + hist_name + '","' + hist_name + '",'+str(scale)+','+str(i-1)+')')
        RFile = R.TFile(RFile_name,'READ')
        chi2_before = RFile.Get(extra + ' SN double').GetFunction(hist_name+'_Func').GetChisquare()
        RFile.Close()

        R.gROOT.ProcessLine('LandauFit("' + RFile_name + '","' + hist_name + '","' + hist_name + '",'+str(scale)+','+str(i+1)+')')
        RFile = R.TFile(RFile_name,'READ')
        chi2_after = RFile.Get(extra + ' SN double').GetFunction(hist_name+'_Func').GetChisquare()
        RFile.Close()

        R.gROOT.ProcessLine('LandauFit("' + RFile_name + '","' + hist_name + '","' + hist_name + '",'+str(scale)+','+str(i)+')')
        RFile = R.TFile(RFile_name,'READ')
        chi2 = RFile.Get(extra + ' SN double').GetFunction(hist_name+'_Func').GetChisquare()
        RFile.Close()
        print chi2_before, chi2, chi2_after

        if (chi2 > chi2_before and chi2 < chi2_after) or (chi2 > chi2_before and chi2 > chi2_after and chi2_before < chi2_after):
            while chi2 >= chi2_before or chi2 > chi2_after or chi2 > 460:
                i -= 1.0
                chi2_after = chi2
                chi2 = chi2_before

                R.gROOT.ProcessLine('LandauFit("' + RFile_name + '","' + hist_name + '","' + hist_name + '",'+str(scale)+','+str(i)+')')
                RFile = R.TFile(RFile_name,'READ')
                chi2_before = RFile.Get(extra + ' SN double').GetFunction(hist_name+'_Func').GetChisquare()
                print chi2, RFile.Get(extra + ' SN double').GetFunction(hist_name+'_Func').GetMaximumX(), i
                RFile.Close()
            i += 1.0

        elif (chi2 < chi2_before and chi2 > chi2_after) or (chi2 > chi2_before and chi2 > chi2_after and chi2_before > chi2_after):
            while chi2 > chi2_before or chi2 >= chi2_after or chi2 > 460:
                i += 1.0
                chi2_before = chi2
                chi2 = chi2_after
        
                R.gROOT.ProcessLine('LandauFit("' + RFile_name + '","' + hist_name + '","' + hist_name + '",'+str(scale)+','+str(i)+')')
                RFile = R.TFile(RFile_name,'READ')
                chi2_after = RFile.Get(extra + ' SN double').GetFunction(hist_name+'_Func').GetChisquare()
                print chi2, RFile.Get(extra + ' SN double').GetFunction(hist_name+'_Func').GetMaximumX(), i
                RFile.Close()
            i -= 1.0

        R.gROOT.ProcessLine('LandauFit("' + RFile_name + '","' + hist_name + '","' + hist_name + '",'+str(scale)+','+str(i+1)+')')
        RFile = R.TFile(RFile_name,'READ')
        chi2_after = RFile.Get(extra + ' SN double').GetFunction(hist_name+'_Func').GetChisquare()
        print chi2, RFile.Get(extra + ' SN double').GetFunction(hist_name+'_Func').GetMaximumX(), i
        RFile.Close()
        
        
    # fit SN no double
    hist_name = extra + ' SN no double'
    print hist_name
    i = start

    R.gROOT.ProcessLine('LandauFit("' + RFile_name + '","' + hist_name + '","' + hist_name + '",'+str(scale)+','+str(i-1)+')')
    RFile = R.TFile(RFile_name,'READ')
    chi2_before = RFile.Get(extra + ' SN no double').GetFunction(hist_name+'_Func').GetChisquare()
    RFile.Close()

    R.gROOT.ProcessLine('LandauFit("' + RFile_name + '","' + hist_name + '","' + hist_name + '",'+str(scale)+','+str(i+1)+')')
    RFile = R.TFile(RFile_name,'READ')
    chi2_after = RFile.Get(extra + ' SN no double').GetFunction(hist_name+'_Func').GetChisquare()
    RFile.Close()

    R.gROOT.ProcessLine('LandauFit("' + RFile_name + '","' + hist_name + '","' + hist_name + '",'+str(scale)+','+str(i)+')')
    RFile = R.TFile(RFile_name,'READ')
    chi2 = RFile.Get(extra + ' SN no double').GetFunction(hist_name+'_Func').GetChisquare()
    RFile.Close()
    print chi2_before, chi2, chi2_after

    if (chi2 > chi2_before and chi2 < chi2_after) or (chi2 > chi2_before and chi2 > chi2_after and chi2_before < chi2_after):
        while chi2 >= chi2_before or chi2 > chi2_after or chi2 > 460:
            i -= 1.0
            chi2_after = chi2
            chi2 = chi2_before

            R.gROOT.ProcessLine('LandauFit("' + RFile_name + '","' + hist_name + '","' + hist_name + '",'+str(scale)+','+str(i)+')')
            RFile = R.TFile(RFile_name,'READ')
            chi2_before = RFile.Get(extra + ' SN no double').GetFunction(hist_name+'_Func').GetChisquare()
            print chi2, RFile.Get(extra + ' SN no double').GetFunction(hist_name+'_Func').GetMaximumX(), i
            RFile.Close()
        i += 1.0

    elif (chi2 < chi2_before and chi2 > chi2_after) or (chi2 > chi2_before and chi2 > chi2_after and chi2_before > chi2_after):
        while chi2 > chi2_before or chi2 >= chi2_after or chi2 > 460:
            i += 1.0
            chi2_before = chi2
            chi2 = chi2_after
        
            R.gROOT.ProcessLine('LandauFit("' + RFile_name + '","' + hist_name + '","' + hist_name + '",'+str(scale)+','+str(i)+')')
            RFile = R.TFile(RFile_name,'READ')
            chi2_after = RFile.Get(extra + ' SN no double').GetFunction(hist_name+'_Func').GetChisquare()
            print chi2, RFile.Get(extra + ' SN no double').GetFunction(hist_name+'_Func').GetMaximumX(), i
            RFile.Close()
        i -= 1.0

    R.gROOT.ProcessLine('LandauFit("' + RFile_name + '","' + hist_name + '","' + hist_name + '",'+str(scale)+','+str(i+1)+')')
    RFile = R.TFile(RFile_name,'READ')
    chi2_after = RFile.Get(extra + ' SN no double').GetFunction(hist_name+'_Func').GetChisquare()
    print chi2, RFile.Get(extra + ' SN no double').GetFunction(hist_name+'_Func').GetMaximumX(), i
    RFile.Close()

    return SignalHist
'''    
RFile = R.TFile('test2.root','RECREATE')
RFile.Close()

file_name1 = sys.argv[1]
file_name2 = sys.argv[2]

scale = 1
region = 3
ped1 = get_preped(file_name1, 'PrePed', 'test2.root',scale)
ped2 = get_pedestal(file_name2, region, ped1, 'R'+str(region),'test2.root',scale)
bad_chans = find_bad_chans(file_name2, region, ped2, '', 'test2.root', scale)
get_signal(file_name2, region, ped2, '', 'test2.root', bad_chans, scale)

print bad_chans
'''
