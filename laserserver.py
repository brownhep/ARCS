import ROOT as R
import socket
import time
from array import array

TCP_IP = '128.148.63.193'
TCP_PORT = 5020
BUFFER_SIZE = 1024



s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
s.send("W0\r\n")
x = s.recv(BUFFER_SIZE)
print "1",x
#time.sleep(1)
s.send("W0\r\n")
x = s.recv(BUFFER_SIZE)
print "2",x
s.send("W1\r\n")
x = s.recv(BUFFER_SIZE)
print "2",x
#time.sleep(1)
s.send("W2\r\n")
x = s.recv(BUFFER_SIZE)
print "3",x
s.send("R0\r\n")
x = s.recv(BUFFER_SIZE)
print "4",x
#s.send("R1\r\n")
#x = s.recv(BUFFER_SIZE)
#print "5",x
#s.send("R2\r\n")
#x = s.recv(BUFFER_SIZE)
#print "6",x
#s.send("A1M1000\r\n")
#x = s.recv(BUFFER_SIZE)
#print "7",x
#s.send("D0\r\n")
#x = s.recv(BUFFER_SIZE)
#print "8",x
#s.send("A0M-33000\r\n")
#x = s.recv(BUFFER_SIZE)
#print "9",x
#for i in xrange(40):
#	s.send("A0M" + str(-1000*i) + "\r\n")
#	x = s.recv(BUFFER_SIZE)
#	print i,x
#	if float(x) != -1000*i: break

s.send("Q\r\n")
#s.close()





