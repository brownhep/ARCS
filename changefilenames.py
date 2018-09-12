import sys

prefixin = "rootfiles/FTH200Y_closesr90_R2/FTH200Y_closesr90_R2"
prefixout = "rootfiles/FTH200Y_reset_R2/FTH200Y_reset_R2"

#+65
instart = 701
outstart = -50
numfiles = 50

shfile = open("changefiles","w")

for i in xrange(numfiles):
	#fileinped = prefixin + "_" + str(i+instart) + "_Ped.dat"
	#fileoutped = prefixout + "_" + str(i+outstart) + "_Ped.dat"
	#fileinsr = prefixin + "_" + str(i+instart) + "_Sr90.dat"
	#fileoutsr = prefixout + "_" + str(i+outstart) + "_Sr90.dat"
	fileinped = prefixin + "_" + str(i+instart) + "_hd.root"
	fileoutped = prefixout + "_" + str(i+outstart) + "_hd.root"
	shfile.write("cp " + fileinped + " " + fileoutped + "\n")
	#shfile.write("cp " + fileinsr + " " + fileoutsr + "\n")
