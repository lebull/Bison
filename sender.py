import RPi.GPIO as GPIO
import time
from tornado.tcpclient import TCPClient
import tornado.ioloop
from tornado import gen

deviceMap = {
    1: 12
}

#Proto Config
P_B1 = 12

SERVER_IP = "192.168.0.102"
PORT = 8990


class IOClient(TCPClient):
    def __init__(self, *args, **kwargs):
        self.button = DirectButton(
            pin = P_B1,
            did = 1,
            onPress = self.onPress,
            onUnPress = self.onUnPress)

        super(TCPClient, self).__init__(*args, **kwargs)

    @gen.coroutine
    def runClient(self):
        print "Connecting to {}:{}".format(SERVER_IP, PORT)
        self.stream = yield TCPClient().connect(SERVER_IP, PORT)
        """
        try:
            while True:
                data = input('(echo) ')
                yield echo(stream, data)
        except KeyboardInterrupt:
            stream.close()
        """


    @gen.coroutine
    def _write(self, message):
        """Send the text to the server and print the reply."""
        if message[-1] != '\n':
            message = message + '\n'
        yield self.stream.write(message.encode('utf-8'))
        print message
        #reply = yield stream.read_until('\n'.encode(options.encoding))
        #print(reply.decode(options.encoding).strip())

    def onPress(self, button):
        self._write("{}, {}".format(button.did, "press"))

    def onUnPress(self, button):
        self._write("{}, {}".format(button.did, "unpress"))

    def tick(self):
        self.button.tick()


class DirectButton:
    def __init__(self, pin, did, onPress=None, onUnPress=None):
        self.pin = pin
        self.did = did

        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


        self.pressed = False
        if(onPress):
            self.setOnPress(onPress)
        if(onUnPress):
            self.setOnUnPress(onUnPress)

    def setOnPress(self, callback):
        self.onPress = callback

    def setOnUnPress(self, callback):
        self.onUnPress = callback

    def _onPress(self):
        if(self.onPress):
            self.onPress(self)

    def onPress(self, button):
        pass

    def _onUnPress(self):
        if(self.onUnPress):
            self.onUnPress(self)

    def onUnPress(self, button):
        pass

    def tick(self):
        pressed = GPIO.input(self.pin) # if port 25 == 1)

        #if the value changes
        if(self.pressed != pressed):
            if(pressed):
                self.onPress(self)
            else:
                self.onUnPress(self)

            self.pressed = pressed

if __name__ == "__main__":
    # @gen.coroutine
    # def run_client():
    #     stream = yield TCPClient().connect(SERVER_IP, PORT)
    #     try:
    #         while True:
    #             data = input('(echo) ')
    #             yield echo(stream, data)
    #     except KeyboardInterrupt:
    #         stream.close()

    client = IOClient()
    tornado.ioloop.PeriodicCallback(client.tick, 50).start()
    client.runClient()
    tornado.ioloop.IOLoop.current().start()
    #tornado.ioloop.IOLoop.instance().run_sync(client.runClient)
    #server.connect("192.168.1.109", "8990")
    # myButton = Button(P_B1)
    #
    # while True:
    #     myButton.tick()
    #     time.sleep(0.001)
