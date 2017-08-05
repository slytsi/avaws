'''
vehicles.py

Class to pull together all parts that operate the vehicle including,
sensors, actuators, pilots and remotes.

Now Includes support for AWS IoT Service using TLSv1.2 over MQTT
'''

import time
from time import sleep
import json
import random
import uuid
import datetime
import paho.mqtt.client as paho
import ssl
import rightfrontwheel
import leftfrontwheel
import rightrearwheel
import leftrearwheel

# Change the endpoint to your AWS IoT service account specific region and id
AwsRestEndpoint = "xxxxxxxxxx.iot.us-east-1.amazonaws.com"
Awsport = 8883

#Certificates
CaPath = "/pathtoCA/VeriSign.pem"
CertPath = "/pathtoThingCert/IoTCert.pem.crt"
KeyPath = "/pathtoThingKey/privateKey.pem.key"

connflag = False

def on_connect(client, userdata, flags, rc):
    global connflag
    connflag = True
    print("Connection returned result: " + str(rc) )


def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    print(Iot_Topic +str(msg.payload))

# Logging can be enabled by uncommenting below

##def on_log(client, userdata, level, buf):
    ##print(msg.topic+" "+str(msg.payload))
    ##print(Iot_Topic +str(msg.payload))    
mqttc = paho.Client()
mqttc.on_connect = on_connect
mqttc.on_message = on_message
#mqttc.on_log = on_log

def getTime():
        currenttime=time.localtime()
        return (time.strftime("%Y%m%d%H%M%S", currenttime))


mqttc.tls_set(CaPath, certfile=CertPath, keyfile=KeyPath, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)
mqttc.connect(AwsRestEndpoint, Awsport, keepalive=60)

#Begin reading sensor telemetry
mqttc.loop_start()


class BaseVehicle:
    def __init__(self,
                 drive_loop_delay = .5,
                 camera=None,
                 actuator_mixer=None,
                 pilot=None,
                 remote=None):

        self.drive_loop_delay = drive_loop_delay #how long to wait between loops

        #these need tobe updated when vehicle is defined
        self.camera = camera
        self.actuator_mixer = actuator_mixer
        self.pilot = pilot
        self.remote = remote

    def start(self):
        start_time = time.time()
        angle = 0.
        throttle = 0.

        #drive loop
        while True:
            now = time.time()
            start = now

            milliseconds = int( (now - start_time) * 1000)

            #get image array image from camera (threaded)
            img_arr = self.camera.capture_arr()

            angle, throttle, drive_mode = self.remote.decide_threaded(img_arr,
                                                 angle, 
                                                 throttle,
                                                 milliseconds)

            if drive_mode == 'local':
                angle, throttle = self.pilot.decide(img_arr)

            if drive_mode == 'local_angle':
                #only update angle from local pilot
                angle, _ = self.pilot.decide(img_arr)

            self.actuator_mixer.update(throttle, angle)

            #print current car state
            end = time.time()
            lag = end - start
            #print('\r CAR: angle: {:+04.2f}   throttle: {:+04.2f}   drive_mode: {}  lag: {:+04.2f}'.format(angle, throttle, drive_mode, lag), end='')          
            
            #Enter in the AWS IoT Topic where you want the vehicle specific information to go.
            vehicle_topic = "/topic/RCTrucks/AVAWS01"

            #Change avawsid to be a unique name
            avawsid = "avaws01"
            #gets time and vehicle specific nformation to add to each json payload
            actualtime = getTime()
            unixtime = str(datetime.datetime.now())
            event = uuid.uuid4()
            eventid= event.hex
            dynamodb_ttl = int(time.time()) + 2592000
            #Change wheel travel to a measurement in inches. 9.5 is default value for magnet rc truck.
            wheel_travel = 9.5
            feet = 12
            wheel_rotations_per_mile = 63360
            speed_reset = random.randint(1,9)
            #Arbitrary batter capacity to simulate battery consumption
            battery_capacity = 5320
            #Wheel calculations from individual wheel python scripts/sensors
            right_front_wheel_rpm = int(rightfrontwheel.get_rpm())
            right_front_wheel_odometer = round((rightfrontwheel.get_distance())/feet,2)
            right_front_wheel_distance = right_front_wheel_rpm * wheel_travel
            right_front_wheel_mpm = right_front_wheel_distance / wheel_rotations_per_mile
            right_front_wheel_mph = right_front_wheel_mpm * 60
            right_front_wheel_speed = round(right_front_wheel_mph)
            right_front_wheel_data = {"right_front_speed" : right_front_wheel_speed , "right_front_rpm" : right_front_wheel_rpm , "right_front_wheel_odometer" : right_front_wheel_odometer}
            left_front_wheel_rpm = int(leftfrontwheel.get_rpm())
            left_front_wheel_odometer = round((leftfrontwheel.get_distance())/feet,2)
            left_front_wheel_distance = left_front_wheel_rpm * wheel_travel
            left_front_wheel_mpm = left_front_wheel_distance / wheel_rotations_per_mile
            left_front_wheel_mph = left_front_wheel_mpm * 60
            left_front_wheel_speed = round (left_front_wheel_mph)
            left_front_wheel_data = {"left_front_speed" : left_front_wheel_speed , "left_front_rpm" : left_front_wheel_rpm , "left_front_wheel_odometer" : left_front_wheel_odometer}

            right_rear_wheel_rpm = int(rightrearwheel.get_rpm())
            right_rear_wheel_odometer = round((rightrearwheel.get_distance())/feet,2)
            right_rear_wheel_distance = right_rear_wheel_rpm * wheel_travel
            right_rear_wheel_mpm = right_rear_wheel_distance / wheel_rotations_per_mile
            right_rear_wheel_mph = right_rear_wheel_mpm * 60
            right_rear_wheel_speed = round(right_rear_wheel_mph)
            right_rear_wheel_data = {"right_rear_speed" : right_rear_wheel_speed , "right_rear_rpm" : right_rear_wheel_rpm , "right_rear_wheel_odometer" : right_rear_wheel_odometer}

            left_rear_wheel_rpm = int(leftrearwheel.get_rpm())
            left_rear_wheel_odometer = round((leftrearwheel.get_distance())/feet,2)
            left_rear_wheel_distance = left_rear_wheel_rpm * wheel_travel
            left_rear_wheel_mpm = left_rear_wheel_distance / wheel_rotations_per_mile
            left_rear_wheel_mph = left_rear_wheel_mpm * 60
            left_rear_wheel_speed = round(left_rear_wheel_mph)
            left_rear_wheel_data = {"left_rear_speed" : left_rear_wheel_speed , "left_rear_rpm" : left_rear_wheel_rpm , "left_rear_wheel_odometer" : left_rear_wheel_odometer}
     
            vehicle_speed = int((right_front_wheel_speed + right_rear_wheel_speed + left_front_wheel_speed + left_rear_wheel_speed)/4)
            average_wheel_rpm = int((right_front_wheel_rpm + right_rear_wheel_rpm + left_front_wheel_rpm + left_rear_wheel_rpm)/4)
            vehicle_odometer = ((right_front_wheel_odometer + right_rear_wheel_odometer + left_front_wheel_odometer + left_rear_wheel_odometer)/4)
            remaining_power = int(battery_capacity - vehicle_odometer)
            engine_rpm = int(average_wheel_rpm * 11)
            angle = round(angle ,4)
            throttle = round(throttle ,4)
            lag = round(lag ,4)
            #Method to reset wheel counter values to 0 when no throttle is applied to simulate the wheels coming to a stop.
            if throttle < 0:
               right_front_wheel_rpm = 0
               right_rear_wheel_rpm = 0
               left_front_wheel_rpm = 0
               left_rear_wheel_rpm = 0
               right_front_wheel_speed = 0
               right_rear_wheel_speed = 0
               left_front_wheel_speed = 0
               left_rear_wheel_speed = 0
               engine_rpm = 0
               vehicle_speed = 0
               average_wheel_rpm = 0
               #Begin creating json payload to deliver to AWS IoT Service Topic
            vehiclepayload = json.dumps (
             {
              "avawsid": avawsid,
              "eventid":eventid,
              "time":actualtime,
              "timestamp" : unixtime,
              "average_wheel_rpm" : average_wheel_rpm,
              "engine_rpm" : engine_rpm,
              "vehicle_speed" : vehicle_speed,
              "vehicle_odometer" : vehicle_odometer,
              "remaining_power" : remaining_power,
              "right_front_wheel_rpm" : right_front_wheel_rpm,
              "left_front_wheel_rpm" : left_front_wheel_rpm,
              "right_rear_wheel_rpm" : right_rear_wheel_rpm,
              "left_rear_wheel_rpm" : left_rear_wheel_rpm,
              "right_front_wheel_speed" : right_front_wheel_speed,
              "left_front_wheel_speed" : left_front_wheel_speed,
              "right_rear_wheel_speed" : right_rear_wheel_speed,
              "left_rear_wheel_speed" : left_rear_wheel_speed,
              "right_front_wheel_odometer" : right_front_wheel_odometer,
              "left_front_wheel_odometer" : left_front_wheel_odometer,
              "right_rear_wheel_odometer" : right_rear_wheel_odometer,
              "left_rear_wheel_odometer" : left_rear_wheel_odometer,
              "dynamodb_ttl" : dynamodb_ttl,
              "angle" :  angle,
              "throttle" : throttle,
              "drive_mode" : drive_mode,
              "lag" : lag       
                   }
             )
            #Print results to console and publish json over MQTT to AWS IoT Service
            print('telemetry payload is ' , vehiclepayload)
            mqttc.publish(vehicle_topic , vehiclepayload ,1)
            time.sleep(self.drive_loop_delay)

