#### wheel mappings ######
## right front wheel 16 ##
## right rear wheel 20 ###
## left front wheel 12 ###
## left rear wheel 5  ####
##########################
import RPi.GPIO as GPIO
import time
from time import sleep
import multiprocessing

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

pulse = 0
distance = 0
rpm = 0.00
speed = 0.00
wheel_in = 9.5
hall = 20
elapse = 0.00

start = time.time()

GPIO.setup(hall, GPIO.IN, pull_up_down = GPIO.PUD_UP)


def get_rpm():
    return rpm

def get_speed():
    return speed

def get_distance():
    return distance

def get_elapse():
    return elapse

def get_pulse(number):
    global elapse,distance,start,pulse,speed,rpm,multiplier
    cycle = 0
    pulse+=1
    cycle+=1
    #rpm = 0
    if pulse > 0:
        elapse = time.time() - start
        print ('pulse is ' , pulse)
        pulse -=1
    if cycle > 0:
        distance += wheel_in
        print ('cycle is ' , cycle)
        cycle -= 1

    if pulse == 0:
       print('pulse is ' , pulse , ' rpm is ',  rpm, 'setting rpm down to 0')
       #rpm = 0
       #elapse = 0
       print ('rpm now is set to ', rpm, ' elapse is set to 0 ' , elapse)
            
    
    rpm = 1/elapse *60
    start = time.time()
    sleep(.001)

try:


    GPIO.add_event_detect(hall,GPIO.FALLING,callback = get_pulse,bouncetime=20)
    #GPIO.cleanup()
except KeyboardInterrupt:
#except elapse < 1:
    GPIO.cleanup()

