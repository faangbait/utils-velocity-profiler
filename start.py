import serial #Read Serial port library
import io # Print to terminal
import os # Manage file system
import struct # Data structure management
import time # Clock
import serial.tools.list_ports as portscan # Find the correct USB port for the anemometer
import RPi.GPIO as GPIO # Manage GPIO Pins
from pololu_drv8835_rpi import motors, MAX_SPEED # Manage motor
import PyGnuplot as gp # Plot data into charts
import numpy as np # Do math with data
currentStep=0 # Always 0 here

#VARIABLES YOU CAN CHANGE THAT WONT CHANGE EVERY TIME
stepsize=2	# HOW FAR BETWEEN CHECKPOINTS
offset=0	# FIRST CHECKPOINT DISTANCE FROM FAN, LESS STEPSIZE (FIRST STEP = OFFSET+STEPSIZE)
stoptime=120	# HOW MANY READINGS TO TAKE AT EACH CHECKPOINT; anemometer sends about 1 reading per second so this is effectively "seconds"
watchdog=600 #Number of Seconds before watchdog is triggered & everything stops; prevents motors stripping

def kick_watchdog():
	global watchdog_t=0

def serial_ports(): # Serial port scanner
	ports=list(portscan.comports())
	for port_no, description, address in ports:
		if 'USB' in description:
			return port_no

def vtplot(filename): # Velocity and temperature plotting function
	gp.c('set term png size 1920,1080')
	gp.c('set output "/var/www/html'+filename+'.png"')
	gp.c('set title "Temp vs Velocity"')
	gp.c('set pointsize 1')
	gp.c('set datafile separator ","')
	gp.c('set yrange [0:2000]') # Y range for Velocity
	gp.c('set y2range [30:100]') # Y range for Temperature
	gp.c('set ytics 50 nomirror tc rgb "blue"')
	gp.c('set ylabel "Velocity (ft/min)" tc lt -1')
	gp.c('set y2tics 5 nomirror tc rgb "red"')
	gp.c('set y2label "Temperature (F)" tc lt -1')
	gp.c('set key above right vertical box 3')
	gp.c('stats "' +filename+'" u 4 nooutput') # Calculate mean for column 4 in csv (Velocity)
	gp.c('set arrow 1 from graph 0, first STATS_mean*196.8504 to graph 1, first STATS_mean*196.8504 nohead') # Draw mean line
	gp.c('set label 1 sprintf("V_m: %0.4f ft/min",STATS_mean*196.8504) at graph 0,1 offset 0,4')
	gp.c('set label 2 sprintf("V_{stddev}: %0.4f ft/min",STATS_stddev*196.8504) at graph 0,1 offset 0,3')
	gp.c('set label 3 sprintf("Confidence Band: %0.1f - %0.1f ft/min",(STATS_mean*196.8504)-(STATS_stddev*196.8504*2),(STATS_mean*196.8504)+(STATS_stddev*196.8504*2)) at graph 0,1 offset 0,2')
	gp.c('plot "'+ filename +'" u ($4*196.8504) w p pt 7 lt rgb "blue" title ("velocity"), "' + filename + '" u ($3*(9/5)+32) w p pt 7 lt rgb "red" title("temperature") axes x1y2')


def end_of_track(channel): # What to do when the track ends
	kick_watchdog()
	time.sleep(.1)
	global reverse
	global currentStep
	if GPIO.input(channel) is GPIO.LOW: # We hit the FRONT side of track
		if reverse:
			reverse = False
			print("Forward")
			currentStep=offset
			motors.setSpeeds(240,240)
			time.sleep(.1)
			GPIO.add_event_detect(20,GPIO.RISING,callback=take_reading,bouncetime=(stoptime+11)*1000)

	else:
		if not reverse:
			reverse = True
			print("Backward")
			GPIO.remove_event_detect(20)
			motors.setSpeeds(MAX_SPEED*-1,MAX_SPEED*-1)

def take_reading(channel):
	kick_watchdog()
	if not reverse:
		motors.setSpeeds(0,0)
		time.sleep(10)
		print("Taking Reading")
		global filename
		global currentStep
		currentStep+=stepsize
		filename = "/home/pi/anemometer/data/"+device+"_"+percent+"per_"+str(currentStep)+"ft.csv"
		port=serial.Serial(serial_ports(),timeout=3)	# OPEN PORT
		for x in range(0,stoptime):			  # HOW MANY READINGS TO TAKE AT EACH SPOT
			time.sleep(.5)			# STOPS FLOODING
			rcv=port.read(40)			# READ DATA
			data=struct.unpack("<2B6f12Bh",rcv)	# PROCESS DATA
			print("TIME: " + time.strftime("%c") + "\t\tTEMP: " + str(data[3]) + "\t\tm/s: " + str(data[2])+"\t\tStep: "+str(currentStep))
			if data[3] > 2 and data[3] < 60: 			# TEMP <2C indicates probable error; do not write to file;
				if data[2] < 30:		# VELO > 30 meters per second indicates probable error, <0.01 probably indicates error, do not write to file
					f = open(filename,"a")
					f.write(time.strftime("%x")+","+time.strftime("%X")+","+str(data[3])+","+str(data[2])+","+str(currentStep)+"\n")
					f.close
				else:
					time.sleep(stoptime)
					break
			else: # if we get a bad reading, all the readings will be bad. stop taking readings to prevent rogue data
				time.sleep(stoptime) #because of the way the debouncer works, we have to stay on this point anyway...
				break
		print("Reading complete - forward")
		motors.setSpeeds(MAX_SPEED,MAX_SPEED)
		vtplot(filename) #Update temp/velocity GNUPlot at end of checkpoint


#INITIALIZE GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(21,GPIO.IN,pull_up_down=GPIO.PUD_DOWN) #GPIO 21 indicates start/end of track
GPIO.setup(20,GPIO.IN,pull_up_down=GPIO.PUD_DOWN) #GPIO 20 indicates checkpoint
#INITIALIZE MOTORS
motors.setSpeeds(0,0)

#GATHER DATA FROM USER
print("//////////////////////////////////////////////////")
print("//        VELOCITY PROFILER V 2.0 SETUP         //")
print("//\t\t\t\t\t\t//")
device=raw_input("// Device Name:")
percent=raw_input("// Percent RPM:")
print("//\t\t\t\t\t\t//")
print("//\t\t\t\t\t\t//");
print("// Step Size: " + str(stepsize) + " Stop Time: " + str(stoptime) + " Offset: " + str(offset))
print("//////////////////////////////////////////////////")

GPIO.add_event_detect(21,GPIO.BOTH,callback=end_of_track,bouncetime=500)

#DETERMINE WHETHER OR NOT WE'RE GOING FORWARD OR BACKWARDS

if GPIO.input(21) is GPIO.LOW:
	print("Switch to Reverse & good to go!")
	reverse = False
else:
	print("Restart in Forward mode")
	reverse = True

#DRIVE
while True:
	time.sleep(.2)
	watchdog_t+=.2 # close enough
	if watchdog_t>watchdog: # Watchdog barks
		motors.setSpeeds(0,0)
		print("Watchdog barks")
		GPIO.remove_event_detect(20)
		GPIO.remove_event_detect(21)

