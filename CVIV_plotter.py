#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#CVIV Raw Data Plotter: IV plot, CV plot (C^-2)
#Original script by Dante Gordon and Soumya Ghosh, with edits by Gabe Altopp
#6/14/17

#############################
#							#
#		  Imports			#
#							#
#############################

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

#############################
#							#
#		  Globals			#
#							#
#############################

testerName = 'Robert_O_'         #Follow name(s) with "_"
cvivDataFiles = 'IV_FTH200Y_01_DiodeS_15_-20C_8_1_2017_4_27_06_PM.txt'
nameForSave = cvivDataFiles.strip('.txt')

if "CV" in cvivDataFiles:
    def pull(cvivFile):
        with open(cvivDataFiles, "r") as cv:
            txtLines = [line for line in cv]
            idx = [i for i, line in enumerate(txtLines) if "BiasVoltage" in line][0]
            headers = txtLines[idx].split('\t')
            cv1kHz_idx = headers.index("LCR_Cp_freq1")
            cv10kHz_idx = headers.index("LCR_Cp_freq2")
            
            
            cv1kHz = []
            cv10kHz = []
            bv = []

            data = txtLines[idx+1:]
            for line in data:
                words = line.split()
                bv.append(words[0])
                cv1kHz.append(words[cv1kHz_idx])
                cv10kHz.append(words[cv10kHz_idx])
            return bv, cv1kHz, cv10kHz
        
    bv, cv1kHz, cv10kHz = pull(cvivDataFiles)
        
    fig = plt.figure(1)
    
    ax = fig.add_subplot(111)
    fig.suptitle('CV_MCZ200Y_05_DiodeS_13')
    ax.plot(bv, cv1kHz, 'ro', label = '1000Hz')
    ax.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.2E'))
    ax.set_xlabel("Bias Voltage (V)")
    ax.set_ylabel("C (F)")
    ax.legend(loc='lower left')
    plt.autoscale(enable=True, axis='y', tight=None)
    
    plt.savefig((testerName + nameForSave) + '.pdf', bbox_inches='tight')
    plt.tight_layout()
    plt.show()
    print(testerName)
        
elif "IV" in cvivDataFiles:
    def pull(cvivFile):
        with open(cvivDataFiles, "r") as iv:
            txtLines = [line for line in iv]
            idx = [i for i, line in enumerate(txtLines) if "BiasVoltage" in line][0]
            headers = txtLines[idx].split('\t')
            iv_idx = headers.index("Current_Avg")
            print(txtLines)

            iv = []
            bv = []

            data = txtLines[idx+1:]
            for line in data:
                words = line.split()
                bv.append(words[0])
                iv.append(str(words[iv_idx]))
            return bv, iv
        
        
    bv, iv = pull(cvivDataFiles)
    
    fig = plt.figure(1)
    fig.suptitle('IV_FTH200Y_01_DiodeS_15')
    ax = fig.add_subplot(111)
    ax.plot(bv, iv, 'ro')
    ax.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.2E'))
    ax.set_xlabel("Bias Voltage (V)")
    ax.set_ylabel("Current (A)")
    plt.autoscale(enable=True, axis='y', tight=None)
    
    plt.savefig((testerName + nameForSave) + '.pdf', bbox_inches='tight')
    plt.show()  
        