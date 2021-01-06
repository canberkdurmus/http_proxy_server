class ProxyRequest:

    def __init__(self, data: bytes):
        self.decoded_data = data.decode()
        print("FROM CLIENT: \n", self.decoded_data)
        lines = [d.strip() for d in self.decoded_data.split("\n") if d.strip()]
        self.method, self.full_path, self.http_version = lines.pop(0).split(" ")
        self.error_message = None
        self.invalid_request = False
        self.conditional_get = False
        self.host, self.port, self.relative = self.parse_url()
        self.http_request = str.replace(self.decoded_data, self.full_path, self.relative, 1).encode('utf-8')

    def parse_url(self):
        if self.method == 'GET':
            http_s, url = self.full_path.split('://')[0], self.full_path.split('://')[1]
            host = url.split('/')[0]
            relative = str.replace(url, host, '')
            domain = host.split(':')[0]
            if domain == 'testlocal':
                domain = 'localhost'
            elif domain == 'localhost':
                pass
            else:
                self.error_message = 'Invalid Host'
                self.invalid_request = True
                return '', '', '/'

            port = host.split(':')[1]

            try:
                port = int(port)
            except ValueError:
                self.error_message = 'Invalid Port'
                self.invalid_request = True
                return '', '', '/'

            return domain, port, relative
        else:
            self.error_message = 'Invalid HTTP Method'
            self.invalid_request = True
            return '', '', '/'

    def check_conditional(self):
        if 'If-Match' in self.decoded_data or "If-None-Match" in self.decoded_data or \
                'If-Modified-Since' in self.decoded_data or 'If-Unmodified-Since' in self.decoded_data \
                or 'If-Range' in self.decoded_data:
            self.conditional_get = True
