from tornado.tcpserver import TCPServer
from tornado.iostream import StreamClosedError
from tornado import gen
import tornado.ioloop

import pyvjoy


PORT = 8990




class EchoServer(TCPServer):

    def __init__(self, *args, **kwargs):
        self.vjoy = pyvjoy.VJoyDevice(1)
        super(EchoServer, self).__init__(*args, **kwargs)

    @gen.coroutine
    def handle_stream(self, stream, address):
        while True:
            try:
                data = yield stream.read_until(b"\n")
                #yield stream.write(data)
                print data

                message = data.split(", ")
                did = int(message[0])
                state = int(message[1])
                print "Setting {} to {}".format(did, state)
                self.vjoy.set_button(did,state)
            except StreamClosedError:
                break

if __name__ == "__main__":
    server = EchoServer()
    server.listen(PORT)
    print "Listening on port {}".format(PORT)
    #server.start()
    tornado.ioloop.IOLoop.current().start()
