import RPi.GPIO as GPIO
import time

#Proto Config
P_B1 = 12

GPIO.setmode(GPIO.BOARD)
GPIO.setup(P_B1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

class Button:
    def __init__(self, pin):
        self.pin = pin
        self.pressed = False
    def onPress(self):
        print "hi"
    def onUnPress(self):
        print "bye"

    def tick(self):
        pressed = GPIO.input(self.pin) # if port 25 == 1)

        #if the value changes
        if(self.pressed != pressed):
            if(pressed):
                self.onPress()
            else:
                self.onUnPress()

            self.pressed = pressed

myButton = Button(P_B1)

while True:
    myButton.tick()
    time.sleep(0.001)
