import os
import argparse
from proxy_socket import proxy_socket


class ProxyServer:
    def __init__(self, port=80, homedir=os.path.curdir):
        self.socket = proxy_socket(port=port)
        self.homedir = os.path.abspath(homedir)

    def serve(self):
        print('Proxy Server is Listening {}:{} in {}'.format(self.socket.host, self.socket.port, self.homedir))
        print("Use 'testlocal' instead of 'localhost' if system overrides proxy settings for localhost \n")
        self.socket.open()
        self.socket.listen()

    def stop(self):
        self.socket.close()


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('port', type=int)
    args = parser.parse_args()

    server = ProxyServer(args.port)
    try:
        server.serve()
    finally:
        server.stop()
