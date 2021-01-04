import mimetypes
import os
import socket
import threading
from BrowserRequest import BrowserRequest


class ServerSocket:
    """Simplified interface for interacting with a web server socket"""
    STATUSES = {
        200: 'Ok',
        404: 'File not found',
    }
    log_format = "{status_code} - {method} {path} {user_agent}"
    response_404 = '<html><h1>404 File Not Found</h1></html>'

    def __init__(self, host='', port=80, buffer_size=1024, max_queued_connections=5):
        self._socket = None
        self.host = host
        self.port = port
        self.buffer_size = buffer_size
        self.max_queued_connections = max_queued_connections
        self.homedir = os.path.abspath(os.path.curdir)
        self.handled = 0

    def __repr__(self) -> str:
        status = 'closed' if self._socket is None else 'open'
        return "<{status} ServerSocket {host}:{port}>".format(status=status, host=self.host, port=self.port)

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def open(self):
        assert self._socket is None, "ServerSocket is already open"
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self._socket.bind((self.host, self.port))
        except Exception as e:
            print(e)
            self.close()
            raise
        else:
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def close(self):
        assert self._socket is not None, "Server Socket is already closed"
        self._socket.close()
        self._socket = None

    def listen(self):
        assert self._socket is not None, "Server Socket must be open to listen data"
        self._socket.listen(self.max_queued_connections)

        while True:
            connection, _ = self._socket.accept()
            print("xd")
            threading.Thread(target=self.response, args=(connection,)).start()

    def response(self, connection):
        data = connection.recv(self.buffer_size)
        request = BrowserRequest(data)
        path = request.path
        try:
            body, status_code = self.load_file(path)
        except IsADirectoryError:
            path = os.path.join(path, 'index.html')
            body, status_code = self.load_file(path)

        header = self.get_header(status_code, path)
        self.respond((header + body).encode(), connection)
        self.handled += 1
        print(self.handled)
        self.log(self.log_format.format(status_code=status_code, method=request.method, path=request.path,
                                        user_agent=request.user_agent))
        return

    def get_header(self, status_code: int, path: str):
        _, file_ext = os.path.splitext(path)
        return "\n".join([
            "HTTP/1.1 {} {}".format(status_code, self.STATUSES[status_code]),
            "Content-Type: {}".format(mimetypes.types_map.get(file_ext, 'application/octet-stream')),
            "Server: SimplePython Server"
            "\n\n"
        ])

    def load_file(self, path):
        try:
            with open(os.path.join(self.homedir, path.lstrip('/'))) as f:
                return f.read(), 200
        except FileNotFoundError:
            return self.response_404, 404

    def respond(self, data: bytes, connection):
        assert self._socket is not None, "Server Socket must be open to respond"
        connection.send(data)
        connection.close()

    @staticmethod
    def log(msg: str):
        print(msg)
