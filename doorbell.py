#!/usr/bin/env python
#vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import time
import RPi.GPIO as GPIO
import datetime
import subprocess
import logging
import fcntl, sys
import signal
import socket
import requests

url = "http://localhost:8123/api/states/switch.doorbell_triggered"
headers = {"Content-Type: application/json"}

data_state_on = "{\"state\": \"on\"}"
data_state_off = "{\"state\": \"off\"}"


logger = logging.getLogger('doorbell')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('/tmp/doorbell.log')
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(ch)
logger.addHandler(fh)

class GracefulKiller:
    kill_now = False
    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)
    def exit_gracefully(self,signum, frame):
        self.kill_now = True

if __name__ == '__main__':

    def play_mp3(path):
        subprocess.Popen(['mpg123', '-q', path]).wait()

    GPIO.setmode(GPIO.BCM)
    DOORBELL_GPIO = 18
    GPIO.setup(DOORBELL_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    RELAIS_1_GPIO = 26 
    GPIO.setup(RELAIS_1_GPIO, GPIO.OUT) # GPIO Modus 
    killer = GracefulKiller()

    try:
        logger.debug("start waiting for input")
        while True:
            if killer.kill_now:
                break

	    if (GPIO.input(DOORBELL_GPIO) == False):
                logger.info(time.strftime("%H:%M:%S") + ' Doorbell rang.\r')
                #fire & forget HASS
                requests.post(url, data=data_state_on, headers={"Content-Type": "application/json"})
                
                GPIO.output(RELAIS_1_GPIO, GPIO.LOW) # activate speaker 
                play_mp3("/home/homeassistant/doorbell.mp3")
                GPIO.output(RELAIS_1_GPIO, GPIO.HIGH) # deactivate speaker 
                time.sleep(0.5)
                requests.post(url, data=data_state_off, headers={"Content-Type": "application/json"})
                
            time.sleep(0.2);
    except KeyboardInterrupt:
        pass
    GPIO.cleanup()
    logger.info("Gracefully closed")
