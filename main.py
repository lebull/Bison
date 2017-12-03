import RPi.GPIO as GPIO
import time

#Proto Config
P_B1 = 12

GPIO.setmode(GPIO.BOARD)
GPIO.setup(P_B1, GPIO.IN, pull_up_down=GPIO.PUD_UP)

while True:
    if(GPIO.input(P_B1)): # if port 25 == 1)
        print "Press"
    print GPIO.input(P_B1)
    time.sleep(0.001)
