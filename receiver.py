from tornado.tcpserver import TCPServer
from tornado.iostream import StreamClosedError
from tornado import gen
import tornado.ioloop

PORT = 8990

class EchoServer(TCPServer):
    @gen.coroutine
    def handle_stream(self, stream, address):
        while True:
            try:
                data = yield stream.read_until(b"\n")
                #yield stream.write(data)
                print data
            except StreamClosedError:
                break

if __name__ == "__main__":
    server = EchoServer()
    server.listen(PORT)
    print "Listening on port {}".format(PORT)
    #server.start()
    tornado.ioloop.IOLoop.current().start()
