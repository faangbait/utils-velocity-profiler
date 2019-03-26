#!/bin/bash

rm stream.dat
touch stream.dat
sudo killall -9 cat
sudo killall -9 readstop.py

sudo chown ss /dev/arduino
sudo chown ss /dev/anemometer1

#Customization Section

stepSize=2
firstStep=5

#End Customization Section

currentStep=$((firstStep-stepSize))

stty -F /dev/arduino cs8 115200 ignbrk -brkint -icrnl -imaxbel -opost -onlcr -isig -icanon -iexten -echo -echoe -echok -echoctl -echoke noflsh -ixon -crtscts
cat /dev/arduino > stream.dat &

while true
do
	data=$(tail -c 1 stream.dat)
	if [ "$data" == "R" ]
	then
		echo "Reverse"
		currentStep=$((firstStep-stepSize))

	elif [ "$data" == "S" ]
	then
		echo "Stopread"
		currentStep=$((currentStep+stepSize))
		./readstop.py $1 $currentStep &

		while [ $data == "S" ]
		do
			data=$(tail -c 1 stream.dat)
		done
		sudo killall -9 readstop.py

	fi
done





bgPid=$!
kill $bgPid
