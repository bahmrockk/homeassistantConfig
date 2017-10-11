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


TCP_IP = '127.0.0.1'
TCP_PORT = 4444 
BUFFER_SIZE = 1024

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

#    s= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#    s.bind((TCP_IP, TCP_PORT))
#    s.listen(1)
#    conn, addr = s.accept()

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(18, GPIO.IN)
    RELAIS_1_GPIO = 26 
    killer = GracefulKiller()
    try:
        logger.debug("start waiting for input")
        while True:
            if killer.kill_now:
                break

	    if (GPIO.input(18) == False):
	        logger.info(time.strftime("%H:%M:%S") + ' Doorbell rang.\r')
                GPIO.setup(RELAIS_1_GPIO, GPIO.OUT) # GPIO Modus 
                GPIO.output(RELAIS_1_GPIO, GPIO.LOW) # activate speaker 
 #               conn.send("ON\n")
                play_mp3("/home/homeassistant/doorbell.mp3")
                GPIO.output(RELAIS_1_GPIO, GPIO.HIGH) # deactivate speaker 
#	        conn.send("OFF\n")
            time.sleep(0.2);
    except KeyboardInterrupt:
        pass
    GPIO.cleanup()
    conn.close()
    logger.info("Gracefully closed")
