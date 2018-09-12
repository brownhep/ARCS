#Code for Plotting the raw CVIV data
#Author: Dante Gordon
#Date Last Modified: 1/31/17

#############################
#							#
#		  Imports			#
#							#
#############################

import linecache
import numpy as np
import pylab as pl
import matplotlib.ticker as ticker
import sys

#############################
#							#
#		  Globals			#
#							#
#############################
bias_voltage = []
avg_current = []
C_freq1 = []
C_freq2 = []
GR_current_avg = []
line_number = 0
total_lines = 0
counter = 0
GR_Connected = False

#file_name = raw_input("Please enter the file to be plotted: ")
file_name = sys.argv[1]

#Code for CV plot
if "CV" in file_name:

	#OPEN FILE
	data_file = open(file_name,"r")

	#1. Find "Bias Voltage (V)" line. This way we know the next line begins all the numbers
	for line in data_file: #for each line in the data file
		line_number = line_number + 1 
		if "BiasVoltage" in line:
			break #once we have found the line we want stop going through the lines	
	
	#Find out if GR is connected or not
	for line in open(file_name, "r"):
		if "GR Current_Avg" in line:
			GR_Connected = True
			break
			
	#Find the total number of lines in the file
	total_lines = sum(1 for line in open(file_name))

	#Find the number of lines left after the "Bias Voltage" line
	lines_leftover = total_lines - line_number
	
	#Find the sensor name and info.
	for line in open(file_name, "r"):
		counter = counter + 1
		if "Sensor Name:" in line:
			line_string = linecache.getline(file_name, counter, None)
			line_strings = line_string.split()
			sensor_name = line_strings[2]
			#print len(line_strings)
		if "Annealing Status:" in line:
			line_string = linecache.getline(file_name, counter, None)
			line_strings = line_string.split()
			annealing = line_strings[2]
		if "Environment:" in line:
			line_string = linecache.getline(file_name, counter, None)
			line_strings = line_string.split()
			temperature = line_strings[1]
			
			
	#2. Fill all of the arrays with the various data in order.
	if GR_Connected == True:
		for n in range(1, lines_leftover + 1):
			line_data = linecache.getline(file_name, line_number + n, None)#gets the nth line of actual numbers
			list_data = line_data.split()#turns the line_data into a list of individual numbers
			bias_voltage.append(list_data[0])#puts the first number into bias_voltage array
			avg_current.append(list_data[1])#puts the second number into the avg_current array
			GR_current_avg.append(list_data[6])#puts the seventh number into the GR_current_avg array
			C_freq1.append(list_data[11])#puts the twelveth (or however you spell it) number into C_freq1 array
			C_freq2.append(list_data[12])#puts the thirteenth number into C_freq2 array
	
	elif GR_Connected == False:
		for n in range(1, lines_leftover + 1):
			line_data = linecache.getline(file_name, line_number + n, None)#gets the nth line of actual numbers
			list_data = line_data.split()#turns the line_data into a list of individual numbers
			bias_voltage.append(list_data[0])#puts the first number into bias_voltage array
			avg_current.append(list_data[1])#puts the second number into the avg_current array
			C_freq1.append(list_data[6])#puts the sixth (or however you spell it) number into C_freq1 array
			C_freq2.append(list_data[7])#puts the seventh number into C_freq2 array
	
	#CLOSE FILE
	data_file.close()


	if GR_Connected == True:
		fig, ax = pl.subplots(2,2)

		pl.suptitle("Sensor " + sensor_name + " at " + temperature + " for " + annealing + "\n")


		ax[0,0].plot(bias_voltage, avg_current, "ro")
		ax[0,0].ticklabel_format(style='sci', axis='y', scilimits=(0,0))#scientific notation on the y-axis
		ax[0,0].set_xlabel("Bias Voltage (V)")#x label
		ax[0,0].set_ylabel("Average Current (A)")#y label
		ax[0,0].xaxis.set_major_locator(ticker.MultipleLocator(100))#major ticks
		ax[0,0].xaxis.set_minor_locator(ticker.MultipleLocator(50))#minor ticks
		
		# ax1.xaxis.set_major_locator(ticker.MultipleLocator(100))#major ticks
# 		ax1.xaxis.set_minor_locator(ticker.MultipleLocator(50))#minor ticks

		ax[0,1].plot(bias_voltage, C_freq1, "ro")
		ax[0,1].plot(bias_voltage, C_freq2, "bo")
		ax[0,1].ticklabel_format(style='sci', axis='y', scilimits=(0,0))#scientific notation on the y-axis
		ax[0,1].set_xlabel("Bias Voltage (V)")#x label
		ax[0,1].set_ylabel("Capacitance (F)")#y label
		ax[0,1].xaxis.set_major_locator(ticker.MultipleLocator(100))#major ticks
		ax[0,1].xaxis.set_minor_locator(ticker.MultipleLocator(50))#minor ticks

		ax[1,0].plot(bias_voltage, GR_current_avg, "ro")
		ax[1,0].ticklabel_format(style='sci', axis='y', scilimits=(0,0))#scientific notation on the y-axis
		ax[1,0].set_xlabel("Bias Voltage (V)")#x label
		ax[1,0].set_ylabel("GR Average Current (A)")#y label
		ax[1,0].xaxis.set_major_locator(ticker.MultipleLocator(100))#major ticks
		ax[1,0].xaxis.set_minor_locator(ticker.MultipleLocator(50))#minor ticks

	elif GR_Connected == False:
	
		pl.suptitle("Sensor " + sensor_name + " at " + temperature + " for " + annealing + "\n")
	
		ax1 = pl.subplot(211) # creates first axis 
		ax1.plot(bias_voltage, avg_current, 'ro')
		ax1.ticklabel_format(style='sci', axis='y', scilimits=(0,0))#scientific notation on the y-axis
		ax1.set_xlabel("Bias Voltage (V)")#x label
		ax1.set_ylabel("Average Current (A)")#y label
		ax1.xaxis.set_major_locator(ticker.MultipleLocator(100))#major ticks
		ax1.xaxis.set_minor_locator(ticker.MultipleLocator(50))#minor ticks
	
	
		ax2 = pl.subplot(212) # creates second axis 
		ax2.plot(bias_voltage, C_freq1, 'bo')
		ax2.plot(bias_voltage, C_freq2, 'go')
		ax2.ticklabel_format(style='sci', axis='y', scilimits=(0,0))#scientific notation on the y-axis
		ax2.set_xlabel("Bias Voltage (V)")#x label
		ax2.set_ylabel("Capacitance (F)")#y label
		ax2.xaxis.set_major_locator(ticker.MultipleLocator(100))#major ticks
		ax2.xaxis.set_minor_locator(ticker.MultipleLocator(50))#minor ticks

	# show the plot on the screen
	print ("GR connected" if GR_connected else "GR disconnected")
        filename = sensor_name + "_" + ("GRconnected" if GR_Connected else "GRdisconnected") + "_" + temperature + "_" + annealing + ".png"
        pl.savefig(filename)
        #`pl.show()
        
#Code for IV plot
elif "IV" in file_name:

	#OPEN FILE
	data_file = open(file_name,"r")

	#1. Find "Bias Voltage (V)" line. This way we know the next line begins all the numbers
	for line in data_file: #for each line in the data file
		line_number = line_number + 1 
		if "BiasVoltage" in line:
			print line_number
			break #once we have found the line we want stop going through the lines	

	#Find the total number of lines in the file
	total_lines = sum(1 for line in open(file_name))

	#Find the number of lines left after the "Bias Voltage" line
	lines_leftover = total_lines - line_number

	#Find the sensor name and info.
	for line in open(file_name, "r"):
		counter = counter + 1
		if "Sensor Name:" in line:
			line_string = linecache.getline(file_name, counter, None)
			line_strings = line_string.split()
			sensor_name = line_strings[2]
			#print len(line_strings)
		if "Annealing Status:" in line:
			line_string = linecache.getline(file_name, counter, None)
			line_strings = line_string.split()
			annealing = line_strings[2]
		if "Environment:" in line:
			line_string = linecache.getline(file_name, counter, None)
			line_strings = line_string.split()
			temperature = line_strings[1]
			


	#2. Fill all of the arrays with the various data in order.
	for n in range(1, lines_leftover + 1):
		line_data = linecache.getline(file_name, line_number + n, None)#gets the nth line of actual numbers
		list_data = line_data.split()#turns the line_data into a list of individual numbers
		bias_voltage.append(list_data[0])#puts the first number into bias_voltage array
		avg_current.append(list_data[1])#puts the second number into avg_current array
		GR_current_avg.append(list_data[6])#puts the seventh number into the GR_current_avg array
	
	#CLOSE FILE
	data_file.close()

	
	#3. Plot the voltage vs. whatever you want
	pl.suptitle("Sensor " + sensor_name + " at " + temperature + " for " + annealing + "\n")
	
	ax1 = pl.subplot(211) # creates first axis 
	ax1.plot(bias_voltage, avg_current, 'ro')
	ax1.ticklabel_format(style='sci', axis='y', scilimits=(0,0))#scientific notation on the y-axis
	ax1.set_xlabel("Bias Voltage (V)")#x label
	ax1.set_ylabel("Average Current (A)")#y label
	ax1.xaxis.set_major_locator(ticker.MultipleLocator(100))#major ticks
	ax1.xaxis.set_minor_locator(ticker.MultipleLocator(50))#minor ticks
	
	
	ax2 = pl.subplot(212) # creates second axis 
	ax2.plot(bias_voltage, GR_current_avg, 'bo')
	ax2.ticklabel_format(style='sci', axis='y', scilimits=(0,0))#scientific notation on the y-axis
	ax2.set_xlabel("Bias Voltage (V)")#x label
	ax2.set_ylabel("GR Average Current (A)")#y label
	ax2.xaxis.set_major_locator(ticker.MultipleLocator(100))#major ticks
	ax2.xaxis.set_minor_locator(ticker.MultipleLocator(50))#minor ticks
	

	# show the plot on the screen
	filename = sensor_name + "_" + "GRconnected" + "_" + temperature + "_" + annealing + ".png"
        pl.savefig(filename)
	#pl.show()



























