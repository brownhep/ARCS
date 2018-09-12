import sys
import os.path

prefix = "FTH200Y_closesr90_R1"
prefixout = "FTH200Y_closesr90_R1"

shfile = open("changefiles","w")

runnum = 0

while os.path.isfile(prefix+"_"+str(runnum)+"_0_Ped.dat"):
	i = 0
	while os.path.isfile(prefix+"_"+str(runnum)+"_0" + str(i) + "_Ped.dat"):

	runnum += 1

#for i in xrange(numfiles):
	fileinped = prefixin + "_" + str(i+instart) + "_Ped.dat"
	fileoutped = prefixout + "_" + str(i+outstart) + "_Ped.dat"
	fileinsr = prefixin + "_" + str(i+instart) + "_Sr90.dat"
	fileoutsr = prefixout + "_" + str(i+outstart) + "_Sr90.dat"
	shfile.write("mv " + fileinped + " " + fileoutped + "\n")
	shfile.write("mv " + fileinsr + " " + fileoutsr + "\n")
