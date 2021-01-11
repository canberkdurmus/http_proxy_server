import os
import socket
import threading
from Request import Request


class SocketManager:
    # All valid HTTP request methods except 'GET'
    VALID_METHODS = [
        'HEAD',
        'POST',
        'PUT',
        'DELETE',
        'CONNECT',
        'OPTIONS',
        'TRACE',
        'PATCH'
    ]
    STATUSES = {
        200: 'OK',
        400: 'Bad Request',
        404: 'Not Found',
        501: 'Not Implemented',
    }
    log_format = "{status_code} - {method} {path}"
    response_200 = '<html><h1>200 OK</h1></html>'
    response_400 = '<html><h1>400 Bad Request</h1></html>'
    response_400_not_int = '<html><h1>400 Bad Request - URI is not integer</h1></html>'
    response_400_low = '<html><h1>400 Bad Request - URI is less than 100</h1></html>'
    response_400_high = '<html><h1>400 Bad Request - URI is greater than 20.000</h1></html>'
    response_404 = '<html><h1>404 Not Found</h1></html>'
    response_501 = '<html><h1>501 Not Implemented</h1></html>'

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
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self._socket.bind((self.host, self.port))
        except Exception as e:
            print(e)
            self.close()
            raise

    def close(self):
        assert self._socket is not None, "Server Socket is already closed"
        self._socket.close()
        self._socket = None

    def listen(self):
        assert self._socket is not None, "Server Socket must be open to listen data"
        self._socket.listen(self.max_queued_connections)

        while True:
            connection, _ = self._socket.accept()
            t = threading.Thread(target=self.response, args=(connection,))
            t.start()

    def response(self, connection):
        data = connection.recv(self.buffer_size)
        request = Request(data)
        body, status_code = self.generate_response(request)
        header = self.get_header(status_code, len(body))
        self.respond((header + body).encode('utf-8'), connection)
        return

    def get_header(self, status_code: int, content_len):
        return "\n".join([
            "HTTP/1.1 {} {}".format(status_code, self.STATUSES[status_code]),
            "Content-Type: text/html; charset=UTF-8",
            "Content-Length: " + str(content_len),
            "Server: CSE4074 HTTP Server"
            "\n\n"
        ])

    def generate_response(self, request):
        if request.method != 'GET':
            if request.method in self.VALID_METHODS:
                # Request method is valid but not get -> 501 Not Implemented
                return self.response_501, 501
            else:
                # Request method is invalid -> 400 Bad Request
                return self.response_400, 400

        try:
            length = int(request.path)
            # Path is greater than 20000 -> 400 Bad Request
            if length > 20000:
                return self.response_400_high, 400
            # Path is less than 100 -> 400 Bad Request
            elif length < 100:
                return self.response_400_low, 400
        # Path is not an int -> 400 Bad Request
        except ValueError:
            return self.response_400_not_int, 400

        current_len = 13
        generated = '<html>'  # len = 6
        while current_len < length:
            generated += 'a'
            current_len += 1
        generated += '</html>'  # len = 7

        return generated, 200

    def respond(self, data: bytes, connection):
        assert self._socket is not None, "Server Socket must be open to respond"
        print("\nSENT: ", data)
        connection.send(data)
        connection.close()

    def log(self, status_code, method, path):
        print(self.log_format.format(status_code=str(status_code), method=str(method), path=str(path)))
