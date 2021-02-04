import os
import argparse
from socket_manager import SocketManager


class Server:
    def __init__(self, port=80, homedir=os.path.curdir):
        self.socket = SocketManager(port=port)
        self.homedir = os.path.abspath(homedir)

    def serve(self):
        print('Listening {}:{} in {}'.format(self.socket.host, self.socket.port, self.homedir))
        self.socket.open()
        self.socket.listen()

    def stop(self):
        self.socket.close()


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('port', type=int)
    args = parser.parse_args()

    server = Server(args.port)
    try:
        server.serve()
    finally:
        server.stop()
