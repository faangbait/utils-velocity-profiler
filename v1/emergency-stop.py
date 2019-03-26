import os
from pololu_drv8835_rpi import motors, MAX_SPEED

print("Emergency stop executed")
motors.setSpeeds(0,0)
os.system("killall -9 python")

