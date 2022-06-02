import socket
import socketserver
import time
import wave
from contextlib import closing
from threading import Thread
import logging

SERVER_ADDRESS = ('localhost', 8686)
logging.basicConfig(level=logging.DEBUG)


class Server():
    def __init__(self):
        # base TCP socket to start the separated UDP dataflow/socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(SERVER_ADDRESS)
        self.server_socket.listen(10)
        self.log = logging.getLogger(__name__)
        self.ACTIVE_THREADS = []

    def start(self):
        conn_handler_thread = Thread(target=self.conn_handler)
        conn_handler_thread.start()
        self.log.info("Server is up and ready for connections")
        while True:
            for thread in self.ACTIVE_THREADS[::]:
                if thread.is_stopped:
                    self.log.debug(f"Thread '{thread}' is down. Remove it.")
                    self.ACTIVE_THREADS.remove(thread)
            time.sleep(1)

    def conn_handler(self):
        while True:
            connection, address = self.server_socket.accept()
            self.log.debug(f"New connection from {address}")
            thr = Handler(connection, address)
            thr.start()
            self.ACTIVE_THREADS.append(thr)

    @staticmethod
    def get_free_port():
        with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as s:
            s.bind(('', 0))
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            print("[get_free_port] Found port: %s " % s.getsockname()[1])
            return s.getsockname()[1]


class Handler(Thread):
    def __init__(self, conn, addr):
        Thread.__init__(self)
        self.conn = conn
        self.addr = addr
        self.is_stopped = False
        self.port = Server.get_free_port()
        self.log = logging.getLogger(__name__)

        self.filename = f"{self.addr[0]}_{self.port}.wav"
        self.wf = wave.open(self.filename, "wb")
        self.server_udp = socketserver.UDPServer(('', self.port), ClientsUDPHandler)
        self.server_udp.wf = self.wf

    def run(self):
        print('[%s:%s] Thread handler created' % self.addr)
        while True:
            thr = None
            data = self.conn.recv(1024)
            if b'start' in data:
                self.conn.send(str(self.port).encode('utf-8'))
                params = data.decode().split(' ')
                channels = int(params[1])
                sample_width = int(params[2])
                frame_rate = int(params[3])

                print("[%s:%s] Start recording. Channels: %s; Sample Width: %s; Frame rate: %s" %
                      (self.addr[0], self.addr[1], channels, sample_width, frame_rate))

                self.wf.setnchannels(channels)
                self.wf.setsampwidth(sample_width)
                self.wf.setframerate(frame_rate)
                thr = Thread(target=self.server_udp.serve_forever)
                thr.start()

            if data == b'stop':
                print("[%s:%s] Stop recording" % self.addr)
                self.is_stopped = True
                self.wf.close()
                self.server_udp.shutdown()
                break

            if not self.conn.fileno():
                print("[%s:%s] Connection closed" % self.addr)
                self.is_stopped = True
                break


class ClientsUDPHandler(socketserver.DatagramRequestHandler):
    def handle(self):
        self.server.wf.writeframes(self.packet)


if __name__=="__main__":
    s = Server()
    s.start()


