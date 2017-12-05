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

class AnalogInput(object):
    def __init__(self, bus, device, channel, outer_deadzone = None):

        self.bus = bus
        self.device = device
        self.channel = channel

        self.odz = 0 #outer deadzone to account for values never reaching 0 or 1 exactly
        if(outer_deadzone):
            self.odz = outer_deadzone


        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)


    def read(self):
        channel = self.channel
        odz = self.odz

        rawData = self.spi.xfer([1, (8 + channel) << 4, 0])
        raw_percentage = round(((rawData[1] * 255 + rawData[2]) / 1024.0), 4)
        adjusted_percentage = (1 + (odz * 2)) * raw_percentage - odz
        clamped_percent = min(max(0, adjusted_percentage), 1)

        return clamped_percent

if __name__ == "__main__":
    pass
