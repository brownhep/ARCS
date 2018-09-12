import ROOT as R
import socket
import time
from array import array

TCP_IP = '128.148.63.68'
TCP_PORT = 5020
BUFFER_SIZE = 1024

c1 = R.TCanvas( 'c1', 'Environmental Data', 200, 10, 700, 500 )

tm = array('f',[0.])
dp = array('f',[0.])
tc = array('f',[0.])
ta = array('f',[0.])
rh = array('f',[0.])
pv = array('f',[0.])
pi = array('f',[0.])

RFile_Name = 'envdata.root'
RTree = R.TTree('env','Environment Data')
RTree.Branch('tm',tm,'tm/F')
RTree.Branch('dp',dp,'dp/F')
RTree.Branch('tc',tc,'tc/F')
RTree.Branch('ta',ta,'ta/F')
RTree.Branch('rh',rh,'rh/F')
RTree.Branch('pv',pv,'pv/F')
RTree.Branch('pi',pi,'pi/F')

j = 1
t0 = 0
data = [[]]

#while True:

data1 = []
#print 'hi'
for i in xrange(7):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((TCP_IP, TCP_PORT))
	s.send(str(i))
	x = s.recv(BUFFER_SIZE)
	data1.append(x)
	print i, x
	s.close()

data.append(data1)

RFile = R.TFile("Env_Web.root",'UPDATE')
RTree = RFile.Get("env").Clone()
#RFile.Close()

if t0 == 0: t0 = float(data1[0])
tm[0] = float(data1[0])-t0
dp[0] = float(data1[1])
tc[0] = float(data1[2])
ta[0] = float(data1[3])
rh[0] = float(data1[4])
pv[0] = float(data1[5])
pi[0] = float(data1[6])
RTree.Fill()

RTree.Draw("dp:tm","","L")
c1.Update()
c1.SaveAs('./public_html/envdata_dp.jpg')
RTree.Draw("tc:tm","","L")
c1.Update()
c1.SaveAs('./public_html/envdata_tc.jpg')
RTree.Draw("ta:tm","","L")
c1.Update()
c1.SaveAs('./public_html/envdata_ta.jpg')
RTree.Draw("rh:tm","","L")
c1.Update()
c1.SaveAs('./public_html/envdata_rh.jpg')
RTree.Draw("pv:tm","","L")
c1.Update()
c1.SaveAs('./public_html/envdata_pv.jpg')
RTree.Draw("pi:tm","","L")
c1.Update()
c1.SaveAs('./public_html/envdata_pi.jpg')

#RFile = R.TFile("Env_Web.root",'RECREATE')
RTree.Write()
c1.Write()
RFile.Close()

#print "received data", data

j+=1

f = open ('./public_html/index.html', 'w')

f.write('<!DOCTYPE html>\n<html>\n<body>\n')
f.write('<center><h1>ARCS Environment</h1></center>\n')
f.write('Last Measurement: ' + str(data1[0]) + '<br>\n')
f.write('<img src="envdata_dp.jpg">\n')
f.write('<img src="envdata_tc.jpg">\n')
f.write('<img src="envdata_ta.jpg">\n')
f.write('<img src="envdata_rh.jpg">\n')
f.write('<img src="envdata_pv.jpg">\n')
f.write('<img src="envdata_pi.jpg">\n')

f.write('</html>\n</body>\n')

#time.sleep(30)



