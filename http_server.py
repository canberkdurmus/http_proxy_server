import os

from ServerSocket import ServerSocket


class SimpleServer:

    def __init__(self, port=80, homedir=os.path.curdir, page404=None):
        """
        Initialize a webserver

        port    -- port to server requests from
        homedir -- path to serve files out of
        page404 -- optional path to HTML file for 404 errors
        """
        self.socket = ServerSocket(port=port)
        self.homedir = os.path.abspath(homedir)
        if page404:
            with open(page404) as f:
                self.response_404 = f.read()

    def serve(self):
        self.socket.open()
        self.socket.log('Opening socket conn {}:{} in {}'.format(self.socket.host, self.socket.port, self.homedir))
        self.socket.listen()

    def stop(self):
        self.socket.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Runs a simple Python server. Not for production')
    parser.add_argument('port', type=int, help='port to run the server on')
    args = parser.parse_args()
    server = SimpleServer(args.port)
    try:
        server.serve()
    finally:
        server.stop()
