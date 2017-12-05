import spidev

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
    import time

    myKnob = AnalogInput(0, 0, 1, 0.005)

    while True:
        print myKnob.read()
        time.sleep(0.5)
