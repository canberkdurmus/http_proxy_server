import os
import socket
import threading
from proxy_request import ProxyRequest


class proxy_socket:
    STATUSES = {
        200: 'OK',
        304: 'Not Modified',
        400: 'Bad Request',
        404: 'Not Found',
        414: 'URI Too Long',
        501: 'Not Implemented',
    }
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
    log_format = "{status_code} - {method} {path}"
    response_200 = '<html><h1>200 OK</h1></html>'
    response_304 = ''
    response_400 = '<html><h1>400 Bad Request</h1></html>'
    response_404 = '<html><h1>404 Not Found</h1></html>'
    response_404_error = '<html><h1>404 Not Found - {error}</h1></html>'
    response_414 = '<html><h1>414 URI Too Long</h1></html>'
    response_501 = '<html><h1>501 Not Implemented</h1></html>'
    cache = {}

    def __init__(self, host='', port=80, buffer_size=1024, max_queued_connections=5):
        self._socket = None
        self.host = host
        self.port = port
        self.buffer_size = buffer_size
        self.max_queued_connections = max_queued_connections
        self.homedir = os.path.abspath(os.path.curdir)

    def __repr__(self) -> str:
        status = 'closed' if self._socket is None else 'open'
        return "<{status} ServerSocket {host}:{port}>".format(status=status, host=self.host, port=self.port)

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def open(self):
        assert self._socket is None, "Socket is already open"
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._socket.bind((self.host, self.port))
        except Exception:
            self.close()
            raise

    def close(self):
        assert self._socket is not None, "Socket is already closed"
        self._socket.close()
        self._socket = None

    def listen(self):
        assert self._socket is not None, "Socket must be open to listen data"
        self._socket.listen(self.max_queued_connections)

        while True:
            connection, _ = self._socket.accept()
            t = threading.Thread(target=self.response, args=(connection,))
            t.start()

    def response(self, connection):
        data = connection.recv(self.buffer_size)
        request = ProxyRequest(data)
        response = self.server_side(request)
        self.respond(response, connection)
        return

    def get_header(self, status_code: int, path: str, content_length):
        _, file_ext = os.path.splitext(path)
        return "\n".join([
            "HTTP/1.1 {} {}".format(status_code, self.STATUSES[status_code]),
            "Content-Type: text/html; charset=UTF-8",
            "Content-Length: " + content_length,
            "Server: CSE4074 HTTP Server"
            "\n\n"
        ])

    def server_side(self, request: ProxyRequest):
        if request.invalid_request:
            header = self.get_header(404, request.full_path, request.full_path)
            return (header + self.response_404_error.format(error=request.error_message)).encode('utf-8')

        try:
            req_length_path = int(request.relative.strip('/'))
        except ValueError:
            header = self.get_header(404, request.full_path, request.full_path)
            return (header + self.response_404_error.format(error='Path is not an integer')).encode('utf-8')

        if req_length_path > 9999:
            header = self.get_header(414, request.full_path, request.full_path)
            return (header + self.response_414).encode('utf-8')

        if request.conditional_get and req_length_path % 2 == 0:
            header = self.get_header(304, request.full_path, request.full_path)
            return (header + self.response_304).encode('utf-8')

        get_cache = self.get_cache(req_length_path)
        if get_cache is not None:
            print("CACHE: ", get_cache)
            return get_cache

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect((request.host, request.port))
        except ConnectionError:
            header = self.get_header(404, request.full_path, request.full_path)
            return (header + self.response_404).encode('utf-8')
        client.send(request.http_request)
        from_server = client.recv(1024)
        client.close()
        print('TO SERVER: \n', request.http_request.decode('utf-8'))
        print("FROM SERVER: ", from_server.decode('utf-8'))

        self.add_cache(req_length_path, from_server)

        return from_server

    def respond(self, data: bytes, connection):
        assert self._socket is not None, "Server Socket must be open to respond"
        print('TO CLIENT: \n', data.decode('utf-8'))
        connection.send(data)
        connection.close()

    def add_cache(self, req, res):
        self.cache[req] = res

    def get_cache(self, req):
        if req in self.cache:
            return self.cache[req]
        else:
            return None
