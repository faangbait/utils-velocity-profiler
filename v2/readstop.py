#!/usr/bin/python3

import serial
import io
import os
import struct
import time
import sys

device="test"
filename="/home/ss/datadump/"+sys.argv[1]+".csv"
port=serial.Serial("/dev/anemometer1",timeout=3)

while 1:
	rcv=port.read(40)
	data=struct.unpack("<2B6f12Bh",rcv)	# PROCESS DATA
	print("TIME: " + time.strftime("%c") + "\t\tTEMP: " + str(data[3]) + "\t\tft/min: " + str(data[2])+"\t\tStep: "+sys.argv[2])
	if data[3] > 2 and data[3] < 120: 			# TEMP <2C indicates probable error; do not write to file;
		if data[2] < 10000 and data[2] > 0:		# VELO > 30 meters per second indicates probable error, <0.01 probably indicates error, do not write to file
			f = open(filename,"a")
			f.write(time.strftime("%x")+","+time.strftime("%X")+","+sys.argv[2]+","+str(data[3])+","+str(data[2])+","+"\n")
			f.close
		else:
			port=serial.Serial("/dev/anemometer1",timeout=3)
	else:
		port=serial.Serial("/dev/anemometer1",timeout=3)

