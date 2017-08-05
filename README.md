# avaws
Fork of https://github.com/wroscoe/donkey to include AWS IoT integration for vehicle drive telemetry.
vehicles.py has been modified to include support for AWS IoT service and individual hall effect sensors at each wheel.
Each wheel file has a different GPIO value based on which GPIO connection the wheel is connected to on the RPi servo hat. 
