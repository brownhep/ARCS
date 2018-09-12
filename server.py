import socket

TCP_IP = '128.148.63.201'
TCP_PORT = 5020
BUFFER_SIZE = 1024


def getenvdata():

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((TCP_IP, TCP_PORT))
	s.send('1')
	data = s.recv(10)
	s.close()

	print "received data", data

getenvdata()
