#TODO: https://stackoverflow.com/questions/9763116/parse-a-tuple-from-a-string
# Parse tuple from string for the type/id combo of the did

from tornado.tcpserver import TCPServer
from tornado.iostream import StreamClosedError
from tornado import gen
import tornado.ioloop

import pyvjoy
import signal
import logging


PORT = 8990

class EchoServer(TCPServer):

    def __init__(self, *args, **kwargs):
        self.vjoy = pyvjoy.VJoyDevice(1)
        self.is_closing = False
        super(EchoServer, self).__init__(*args, **kwargs)

    @gen.coroutine
    def handle_stream(self, stream, address):
        while True:
            try:
                data = yield stream.read_until(b"\n")
                #yield stream.write(data)


                message = self.parseMessage(data)

                did_raw = message[0]
                did_type = str(did_raw[0].replace("'",""))
                did_number = int(did_raw[1])
                state = float(message[1][0])
                print "Setting {} {} to {}".format(did_type, did_number, state)

                if(did_type == "a"):
                    dev = pyvjoy.HID_USAGE_Z
                    val = int(state * 0x8000)
                    #val = "{0:#0{1}x}".format(val,6)
                    #val = 0x4000
                    print "DEBUG: {}, {}".format(dev, val)
                    self.vjoy.set_axis(dev, val)
                    #self.vjoy.update()

                else:
                    print "\n{}\n".format(state)

                    self.vjoy.set_button(did_number,int(state))
            except StreamClosedError:
                break

    def parseMessage(self, message):

        messageParts = message.rsplit(",", 1)
        for i in range(len(messageParts)):
            messageParts[i] = messageParts[i]    \
                .replace("(", "")   \
                .replace(")", "")   \
                .replace(" ", "")   \
                .replace(r"\n", "")  \
                .split(",")

        return messageParts[0], messageParts[1]

    def _try_exit(self):
        if self.is_closing:
            # clean up here
            tornado.ioloop.IOLoop.instance().stop()
            logging.info('exit success')

    def _signal_handler(self, signum, frame):
        logging.info('exiting...')
        self.is_closing = True

if __name__ == "__main__":
    server = EchoServer()
    server.listen(PORT)
    print "Listening on port {}".format(PORT)
    #server.start()
    signal.signal(signal.SIGINT, server._signal_handler)
    tornado.ioloop.PeriodicCallback(server._try_exit, 100).start()
    tornado.ioloop.IOLoop.current().start()
