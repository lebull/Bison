
import time
from tornado.tcpclient import TCPClient
import tornado.ioloop
from tornado import gen

from BisonInput import DirectButton, AnalogInput, ButtonChain

deviceMap = {
    1: 12
}

#Proto Config
P_B1 = 12

#SERVER_IP = "192.168.0.102"
SERVER_IP = "192.168.1.105"
PORT = 8990


class IOClient(TCPClient):
    def __init__(self, *args, **kwargs):


        self.buttonChain = ButtonChain(
            frequency=5000,
            cycles = 66,
            didOffset = 2,
            onPress = self.onPress,
            onUnPress = self.onUnPress)


        self.button = DirectButton(
            pin = P_B1,
            did = ("b", 1),
            onPress = self.onPress,
            onUnPress = self.onUnPress)

        self.knob = AnalogInput(
            did = ("a", 1),
            bus = 0,
            device = 0,
            channel = 1,
            outer_deadzone = 0.005,
            onChange = self.onAxis)

        #self.buttonChain = ButtonChain()

        super(TCPClient, self).__init__(*args, **kwargs)

    @gen.coroutine
    def runClient(self):
        print "Connecting to {}:{}".format(SERVER_IP, PORT)
        self.stream = yield TCPClient().connect(SERVER_IP, PORT)

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
        self._write("{}, {}".format(button.did, "1"))

    def onUnPress(self, button):
        self._write("{}, {}".format(button.did, "0"))

    def onAxis(self, axis):
        self._write("{}, {}".format(axis.did, axis.getValue()))

    def tick(self):
        self.buttonChain.sweep()
        self.button.tick()
        self.knob.tick()


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
    tornado.ioloop.PeriodicCallback(client.tick, 20).start()
    client.runClient()
    #tornado.ioloop.IOLoop.instance().run_sync(client.runClient)
    tornado.ioloop.IOLoop.current().start()
    #tornado.ioloop.IOLoop.instance().run_sync(client.runClient)
    #server.connect("192.168.1.109", "8990")
    # myButton = Button(P_B1)
    #
    # while True:
    #     myButton.tick()
    #     time.sleep(0.001)
