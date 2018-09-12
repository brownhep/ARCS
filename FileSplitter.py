import sys
import os.path

def splitfile(filein, fileout1, fileout2, numevents):

    
    firstfile = True
    event = 0
    pedfile = open(filein + "_Ped.dat",'r')
    pedout1 = open(fileout1 + "_Ped.dat", "w")

    for line in pedfile:
	
	if firstfile:  pedout1.write(line)
	else: pedout2.write(line)

        #Only looks at lines with data in them
        if line.count(',') > 3:
            event += 1 #increments the event count
            if event % 4000 == 0: print event/4 #Prints status

	if event > numevents:
		firstfile = False
		pedout1.close()
    		pedout2 = open(fileout1 + "_Ped.dat", "w")

    pedout2.close()

    firstfile = True
    event = 0
    srcfile = open(filein + "_Sr90.dat",'r')
    srcout1 = open(fileout1 + "_Sr90.dat", "w")

    for line in srcfile:
	
	if firstfile:  srcout1.write(line)
	else: srcout2.write(line)

        #Only looks at lines with data in them
        if line.count(',') > 3:
            event += 1 #increments the event count
            if event % 4000 == 0: print event/4 #Prints status

	if event > numevents:
		firstfile = False
		srcout1.close()
    		srcout2 = open(fileout1 + "_Sr90.dat", "w")

    srcout2.close()


    return event


for i in xrange(8):
	fileinprefix = "FTH200Y_reset_R2_1_" + str(i)
	fileout1prefix = "FTH200Y_reset_R2_1_" + str(i)
	fileout2prefix = "FTH200Y_reset_R7_2_" + str(i)
	splitfile(fileinprefix, fileout1prefix, fileout2prefix, 10000)
