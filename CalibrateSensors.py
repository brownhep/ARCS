import ROOT as R
import sys
import time
import os.path
from datetime import datetime, date, time, timedelta
from array import array

def get_tempdata_cal(file_name, outfolder, filePrefix):

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

    #Opens environmental data file
    print "Reading in environmental data from file: ", file_name
    if os.path.isfile(file_name):
        env_file = open(file_name,'r')
        cnt = 0
        #temp_data = [[0 for x in xrange(7)]]
	temp_data = []
        t_data = [0 for x in xrange(7)]
        for line in env_file:
            env_data = line.split('\t')
            for i in xrange(7): t_data[i] = float(env_data[i])
	    #print t_data
            temp_data.append([])
            for i in xrange(7): temp_data[cnt].append(t_data[i])
	    #print temp_data
            time[0] = float(env_data[0])/(60*60*24) - 40500
            dewp[0] = float(env_data[1])
            chuckT[0] = float(env_data[2])
            airT[0] = float(env_data[3])
            RH[0] = float(env_data[4])
            Vpelt[0] = float(env_data[5])
            Ipelt[0] = float(env_data[6])
            RTree.Fill()
            cnt += 1

        RFile = R.TFile(outfolder+filePrefix+"_Env.root",'RECREATE')
        RTree.Write()
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
                chuckT = [Ti0 + (time-ti0)*(Ti-Ti0)/(ti-ti0),i-1]
                break

    return chuckT


def cal_sensor(fileprefix, scale = 1, T_Array=0):

    file_name = fileprefix + ".dat"
    RFile_name = fileprefix + ".root"
    file = open(file_name, 'r')
    
    Data = R.TProfile2D('Data','Data',512,0,512,32,0,32)
    Data.Sumw2()
    Data.SetOption('colz')

    HGain = R.TH1D('Gain','Gain',512,0,512)
    HOffset = R.TH1D('Offset','Offset',512,0,512)
    HChi2 = R.TH1D('Chi2','Chi2',512,0,512)
    HBadCh = R.TH1D('BadCh','Bad Channels',512,0,512)
    HNsyCh = R.TH1D('NsyCh','Noisy Channels',512,0,512)
    HDisconCh = R.TH1D('DisconCh','Disconnected Channels',512,0,512)

    ical = array('i', [0])
    strip = array('i', [0])
    charge = array ('f', [0.])
    T_Chuck = array ('f', [0.])
    gain = array ('f', [0.])
    offset = array ('f', [0.])
    chi2 = array ('f', [0.])

    #Creates TObject to store time
    StartTime = R.TVectorF(1)
    StartTemp = R.TVectorF(1)
    
    RTree = R.TTree('rawcal', 'Raw Calibration Data')
    RTree.Branch('ical',ical,'ical/I')
    RTree.Branch('strip',strip,'strip/I')
    RTree.Branch('charge',charge,'charge/F')
    RTree.Branch('T_Chuck',T_Chuck,'T_Chuck/F')

    RTree2 = R.TTree('cal', 'Gain/Offset Calibration Data')
    RTree2.Branch('strip',strip,'strip/I')
    RTree2.Branch('gain',gain,'gain/F')
    RTree2.Branch('offset',offset,'offset/F')
    RTree2.Branch('chi2',chi2,'chi2/F')

    event_data = []
    bad_chan = []
    StartTemp[0] = -99.0
    event = 0
    Tindex = 0

    for line in file:
        #Read out time from file
        if line[0:4] == 'Date':
            rdate = line.split(' ')[1].split('.')
            rtime = line.split(' ')[3].split(':')
            runtime = datetime(2000+int(rdate[2]),int(rdate[1]),int(rdate[0]),int(rtime[0]),int(rtime[1]),int(rtime[2])) - datetime(1904,1,1,0,0,0,0)
            lvtime = 24*60*60*float(runtime.days) + float(runtime.seconds/86400.00000)
            print rdate, rtime, runtime, runtime.seconds, lvtime

        if line.count(',') > 3:
            event += 1
	    if event % 4 == 1:
	    	tmstamp = float(line.split('\t')[0])
		tca = get_temp (T_Array, tmstamp, Tindex)
		T_Chuck[0] = tca[0]
		Tindex = tca[1]
		if StartTemp[0] < 90: StartTemp[0] = T_Chuck[0]

            #if event % 100 == 0: print "ICAL, CDRV ", ical[0], cdrv
            if event % 8000 == 0: print "ICAL: ", event, ical_step
		
            full_event = [float(x) for x in line.replace('\r\t','').split('\t')[-1].split(',')]
            if scale != 1: event_data += [x*192000.0/full_event[-1] for x in full_event[12:-1]]
            else: event_data += full_event[12:-1]
            
            if event % 4 == 0:
		eventno = event/4
            	ical_step = eventno/800
            	cdrv = int((eventno - 800*ical_step)/100)
                #subtracted_event = [event_data[i] - Ped.GetBinContent(i+1) for i in range(512)]
                #apv_event = subtracted_event[(region+1)/4*128:(1+(region+1)/4)*128]
                #reg_event = subtracted_event[32*(region+1):32*(region+2)]
                
                for i in xrange(64):
                    stp = cdrv + 8*i
                    Data.Fill(stp, ical_step, event_data[stp])

                event_data = []

    file.close()

    #Fill tree with averages from profile histogram
    for i in xrange(512):
    	h1 = R.TH1D('FitProfile','Fit Profile',32,0,256)
    	f1 = R.TF1()
	lf = R.TLinearFitter(1)
	for j in xrange(32):
		ical[0] = 8*j
		strip[0] = i
		charge[0] = Data.GetBinContent(i+1,j+1)
		RTree.Fill()
		h1.Fill(ical[0],charge[0])
		#lf.AddPoint(8.0*j,charge[0],1)
	h1.Fit("pol1")
	f1 = h1.GetFunction("pol1")
	strip[0] = i
	gain[0] = f1.GetParameter(1)
	offset[0] = f1.GetParameter(0)
	chi2[0] = f1.GetChisquare()
	if chi2[0] > 12: 
		HNsyCh.Fill(i,1)
		bad_chan.append(i)
	if gain[0] < 0.1: 
		HBadCh.Fill(i,1)
		bad_chan.append(i)
	if gain[0] > 0.6 and chi2[0] > 4: HDisconCh.Fill(i,1)
	HGain.Fill(i,gain[0])
	HOffset.Fill(i,offset[0])
	HChi2.Fill(i,chi2[0])
	RTree2.Fill()
	print f1.GetParameter(0), f1.GetParameter(1), f1.GetChisquare()
	h1.Delete()
	

    if RFile_name != '':
        RFile = R.TFile(RFile_name,'RECREATE')
        StartTime[0] = tmstamp/(60*60*24) - 40500 #Get time in days since Jan 1, 1904 + 40500 days
        StartTime.Write("StartTime")
	StartTemp.Write("StartTemp")
	Data.Write()
	HGain.Write()
	HOffset.Write()
	HChi2.Write()
	HNsyCh.Write()
	HBadCh.Write()
	HDisconCh.Write()
        RTree.Write()
        RTree2.Write()
        RFile.Close()

    return bad_chan

#cal_sensor("FTH200Y_20C_lat192_Cal")
#cal_sensor("FTH200Y_20C_lat193_Cal")
