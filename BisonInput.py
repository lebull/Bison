import RPi.GPIO as GPIO

class Button(object):
    """
        Abstract button or input device.  Mainly handles the press/unpress events.
        Should it be release instead of unpress?  Heck if I know...

        did = device_id.  If I'm lucky, these will map to the vjoy inputs.
    """
    def __init__(self, did, onPress=None, onUnPress=None):
        self.did = did
        self.pressed = False
        if(onPress):
            self.setOnPress(onPress)
        if(onUnPress):
            self.setOnUnPress(onUnPress)

    def setPressed(self, pressed):
        #if the value changes
        if(self.pressed != pressed):
            if(pressed):
                self.onPress(self)
            else:
                self.onUnPress(self)
            self.pressed = pressed

    def setOnPress(self, callback):
        self.onPress = callback

    def setOnUnPress(self, callback):
        self.onUnPress = callback

    def _onPress(self):
        if(self.onPress):
            self.onPress(self)

    def onPress(self, button):
        """ Placeholder press event """
        pass

    def _onUnPress(self):
        if(self.onUnPress):
            self.onUnPress(self)

    def onUnPress(self, button):
        """ Placeholder unpress event """
        pass


class DirectButton(Button):
    """
        Reads a gpio pin directly as the value of the button.  This is a shitty
        blocking implimentation, but idc
    """
    def __init__(self, pin, *args, **kwargs):
        self.pin = pin

        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        super(DirectButton, self).__init__(*args, **kwargs)

    def tick(self):
        self.setPressed( GPIO.input(self.pin) )



if __name__ == "__main__":
    pass
