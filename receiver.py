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
                print data

                message = data.split(", ")
                did_raw = int(message[0])
                did_type = did[0]
                did = did[1]
                state = int(message[1])
                print "Setting {}{} to {}".format(did_type, did, state)

                if(did_type == "a"):
                    self.vjoy.set_axis(HID_USAGE_X,state * 0x8000)
                else:
                    self.vjoy.set_button(did,state)
            except StreamClosedError:
                break



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
