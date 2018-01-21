#TODO:  Set a trigger threshold for change event for analog inputs

import RPi.GPIO as GPIO
import spidev
import time
import os

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
    def __init__(self, did, bus, device, channel, outer_deadzone = None, onChange = None):

        self.value = 0

        self.did = did
        self.bus = bus
        self.device = device
        self.channel = channel

        self.odz = 0 #outer deadzone to account for values never reaching 0 or 1 exactly
        if(outer_deadzone):
            self.odz = outer_deadzone

        if(onChange):
            self.onChange = onChange

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

    def getValue(self):
        return self.value

    def setValue(self, value):
        if(value != self.value):
            self.value = value
            self._onChange()

    def _onChange(self):
        self.onChange(self)

    def onChange(self, analogInput):
        """Placeholder change event"""
        pass

    def tick(self):
        self.setValue( self.read() )


class PoorCycle(object):
    def __init__(self, cycles, frequency=10):
        self.callbacks = {}
        self.allTicksCallbacks = []
        self.cycles = cycles
        self.frequency = frequency
        self.n = 0

        print frequency

    def registerTick(self, callback, tick=None):

        if(not tick):
            self.allTicksCallbacks.append(callback)
        else:
            if(not tick in self.callbacks):
                self.callbacks[tick] = []
            self.callbacks[tick].append(callback)

    def rise(self):
        pass
    def fall(self):
        pass

    def tick(self):
        if(self.n == round(self.n)):
            self.fall()
        else:
            self.rise()

        #if self.n in self.callbacks:
        #    for callback in self.callbacks[self.n]:
        #        callback()

        for callback in self.allTicksCallbacks:
            callback()

    def reset(self):
        self.n = 0

    def sweep(self):
        self.n = 0
        while(self.n <= self.cycles):


            self.tick()
            self.n += 0.5
            time.sleep(1.0/(self.frequency*2))


    def run(self):
        while True:
            self.sweep()


if __name__ == "__main__":
    pass

class ButtonChain(PoorCycle):

    """
        Reads a gpio pin directly as the value of the button.  This is a shitty
        blocking implimentation, but idc
    """
    def __init__(self, frequency=10, cycles = 10, didOffset = 0, onPress = None, onUnPress = None, *args, **kwargs):

        print frequency

        self.DIDTYPE = "b" #axis, cause I was derpy one night

        self.didOffset = didOffset

        super(ButtonChain, self).__init__(cycles, frequency, *args, **kwargs)

        self.buttons = {}
        for i in range(cycles):
            buttonDid = (str(self.DIDTYPE), self.didOffset + i)
            self.buttons[buttonDid] = Button(did=buttonDid, onPress=onPress, onUnPress=onUnPress)

        # self.pins = {
        #     "SER":   29, #Data In
        #     "OE":    31, #Output Enable
        #     "RCLK":  33, #Shift Clock
        #     "SRCLK": 36, #Shift Register Clock (Move shift reg to reg)
        #     "SRCLR": 37  #Shift Register Clear
        # }

        self._setuptOutput()

        self.pins = {
            "SER":   37, #Data In
            "OE":    35, #Output Enable
            "RCLK":  33, #Register Clock (Move shift reg to reg)
            "SRCLK": 31, #Shift Register Clock (Shift)
            "SRCLR": 29  #Shift Register Clear
        }

        self.readPin = 40

        GPIO.setmode(GPIO.BOARD)
        for (name, pinid) in self.pins.iteritems():
            GPIO.setup(pinid, GPIO.OUT)
        GPIO.setup(self.readPin, GPIO.IN)
        GPIO.output(self.pins["OE"], GPIO.LOW)
        GPIO.output(self.pins["SRCLR"], GPIO.HIGH)

        #self.registerTick(self.tick)

        #self.rclk =  GPIO.PWM(self.pins["RCLK"], self.freq)
        #self.srclk = GPIO.PWM(self.pins["SRCLK"], self.freq)

    def _setuptOutput(self):
        self.output = [False] * (self.cycles - 2)

    def rise(self):
        GPIO.output(self.pins["RCLK"], GPIO.LOW)
        GPIO.output(self.pins["SRCLK"], GPIO.HIGH)
        self.debug()

    def fall(self):
        GPIO.output(self.pins["RCLK"], GPIO.HIGH)
        GPIO.output(self.pins["SRCLK"], GPIO.LOW)
        self.debug()

    def _halfTickDuration(self):
        return 1.0/(self.freq*2)

    def tick(self,*args, **kwargs):

        super(ButtonChain, self).tick(*args, **kwargs)

        #time.sleep(0.1)

        #On the upbeat
        if self.n != int(self.n):

            i = int(self.n)
            if(i >= 0 and i < self.cycles-1):
                oldVal = self.output[i-1]
                newVal = GPIO.input(self.readPin)
                if(oldVal != newVal):
                    #print self.n
                    #k = i - 1
                    self.buttons[(self.DIDTYPE, self.didOffset + i )].setPressed(newVal)
                    print "{}:\t{}".format(i, newVal)
                    # if(newVal):
                    #     print "{} pressed".format(k)
                    #     #self.buttons[k].onPress()
                    # else:
                    #     print "{} released".format(k)
                    #     #self.button[k].onUnPress()

                self.output[i - 1] = GPIO.input(self.readPin)

        #On the last tick
        # if(self.n == self.cycles):
        #     #GPIO.output(self.pins["SER"], GPIO.HIGH)
        #     print "\n" * 50
        #     print self.output

        #on the First tick
        if(self.n == 0):
            #GPIO.output(self.pins["SRCLR"], GPIO.LOW)

            GPIO.output(self.pins["SER"], GPIO.HIGH)
        #On every tick but the first one
        else:
            #GPIO.output(self.pins["SRCLR"], GPIO.HIGH)
            GPIO.output(self.pins["SER"], GPIO.LOW)

    def debug(self):
        return
        print "\n" * 50
        print "{}:\n".format(self.n)
        for (name, pinid) in self.pins.iteritems():
            print "{}\t{}".format(name, GPIO.input(pinid))
